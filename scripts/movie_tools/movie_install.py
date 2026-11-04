"""Standalone source-bound movie verify/install/restore (Python 3.10+).

Close the game first. Production needs an exactly approved bundle and complete
render receipt. Developer QA requires the conspicuous --developer-qa-install
opt-in (CLI --qa-install). This tool neither renders movies nor changes approval flags.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import uuid

from movie_bundle import file_hash, json_bytes
from movie_render import validate_bundle
from fix_movie_vbv import patch_headers, VBV_VALUE

MAX_MOVIE_BYTES = 512 * 1024 * 1024
TEMP_SUFFIX = '.saihate-movie-tmp'
LOCK = 'saihate-no-ima-install.lock'


def strict_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON field')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def safe_path(path, file=False):
    path = Path(os.path.abspath(path))
    for item in reversed((path, *path.parents)):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError(f'Links/junctions are not supported: {item}')
        if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
            raise ValueError(f'Hard-linked files are not supported: {item}')
    if file and not path.is_file():
        raise ValueError(f'Required regular file is missing: {path}')
    return path


def writable(path):
    info = path.stat()
    if getattr(info, 'st_file_attributes', 0) & 1 or not stat.S_IMODE(info.st_mode) & 0o222:
        raise ValueError(f'Read-only destination; permissions were not changed: {path}')


def exclusive_bytes(path, data):
    safe_path(path)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0)
    with os.fdopen(os.open(path, flags, 0o600), 'wb') as target:
        target.write(data)
        target.flush()
        os.fsync(target.fileno())


def copy_exclusive(source, target, expected_hash):
    source, target = safe_path(source, True), safe_path(target)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0)
    with source.open('rb') as incoming, os.fdopen(os.open(target, flags, 0o600), 'wb') as outgoing:
        for block in iter(lambda: incoming.read(1024 * 1024), b''):
            outgoing.write(block)
        outgoing.flush()
        os.fsync(outgoing.fileno())
    if file_hash(target) != expected_hash or file_hash(source) != expected_hash:
        raise ValueError('Streaming copy/source verification failed; partial bytes retained')


def checked_hash(path, expected, size=None):
    path = safe_path(path, True)
    if not 0 < path.stat().st_size <= MAX_MOVIE_BYTES or (size is not None and path.stat().st_size != size):
        raise ValueError(f'Unsupported movie size: {path}')
    if file_hash(path) != expected:
        raise ValueError(f'Movie checksum mismatch: {path}')
    return path


def load_binding(bundle, renders, developer_qa=False, require_renders=True):
    bundle, renders = safe_path(bundle), safe_path(renders)
    manifest_path = safe_path(bundle / 'movie-bundle.json', True)
    strict_json(manifest_path)
    # Additionally reject Windows reparse points on every consumed track.
    for number in range(3):
        safe_path(bundle / f'movie-{number:02d}.ass', True)
    manifest = validate_bundle(bundle, developer_qa)
    receipt_path = safe_path(renders / 'movie-render-receipt.json', True)
    receipt = strict_json(receipt_path)
    if (receipt.get('schema') != 'saihate-movie-render-receipt-v1'
            or receipt.get('render_complete') is not True
            or type(receipt.get('qa_only')) is not bool
            or receipt['qa_only'] != manifest['qa_only']
            or receipt.get('installed') is not False
            or receipt.get('bundle_sha256') != file_hash(manifest_path)):
        raise ValueError('Receipt is incomplete, unapproved, or belongs to a different bundle')
    rows = receipt.get('movies')
    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError('Receipt must bind all three exact movie outputs')
    targets = []
    for entry, row in zip(manifest['movies'], rows):
        if not isinstance(row, dict) or any(row.get(key) != entry[key] for key in
                ('movie', 'source_sha256', 'subtitle_track_sha256')):
            raise ValueError('Receipt movie/source/track binding differs')
        if (type(row.get('size_bytes')) is not int or not 0 < row['size_bytes'] <= MAX_MOVIE_BYTES
                or not isinstance(row.get('sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', row['sha256'])
                or type(row.get('video_frames')) is not int
                or row['video_frames'] != entry['expected_video_frames']
                or row.get('audio_packet_sha256') != entry['expected_audio_packet_sha256']
                or row.get('full_decode_passed') is not True):
            raise ValueError('Receipt technical frame/audio/decode proof differs')
        times = [float(row[key]) for key in ('video_start_seconds', 'audio_start_seconds')]
        if not all(math.isfinite(t) and t >= 0 for t in times) or abs(times[0] - times[1]) > 1 / 90000:
            raise ValueError('Receipt has invalid audio/video alignment')
        fonts = row.get('font_selection')
        if not isinstance(fonts, list) or not fonts or any(not isinstance(line, str) or
                'fontselect:' not in line or line.rsplit(',', 1)[-1].strip() not in
                ('Arial', 'ArialMT', 'Arial-Regular') for line in fonts):
            raise ValueError('Receipt has no exact Arial rendering evidence')
        render = safe_path(renders / row['movie'])
        if require_renders:
            checked_hash(render, row['sha256'], row['size_bytes'])
        targets.append({'movie': row['movie'], 'path': entry['source_path'],
                        'source_sha256': row['source_sha256'],
                        'output_sha256': row['sha256'], 'output_size': row['size_bytes']})
    binding = {'schema': 'saihate-transactional-movie-binding-v1', 'qa_only': manifest['qa_only'],
               'bundle_sha256': file_hash(manifest_path), 'receipt_sha256': file_hash(receipt_path),
               'targets': targets}
    binding_hash = hashlib.sha256(json_bytes(binding)).hexdigest()
    return renders, binding, binding_hash


def inspect_targets(game, binding):
    game = safe_path(game)
    hd = safe_path(game / 'HD')
    if not game.is_dir() or not hd.is_dir():
        raise ValueError('Expected a user-owned game directory with HD')
    writable(game)
    writable(hd)
    states = []
    for row in binding['targets']:
        target = safe_path(game / row['path'], True)
        writable(target)
        size = target.stat().st_size
        if not 0 < size <= MAX_MOVIE_BYTES:
            raise ValueError('Unsupported installed movie size')
        sha = file_hash(target)
        if sha == row['source_sha256']:
            state = 'source'
        elif sha == row['output_sha256'] and size == row['output_size']:
            state = 'output'
        elif size == row['output_size'] and is_header_repaired(target, row['output_sha256']):
            state = 'output-repaired'
        else:
            raise ValueError(f'Wrong edition or unknown changed movie; untouched: {target}')
        temporary = safe_path(Path(str(target) + TEMP_SUFFIX))
        if temporary.exists() and (not temporary.is_file() or temporary.stat().st_size > MAX_MOVIE_BYTES):
            raise ValueError('Unsupported interrupted temporary file')
        states.append((row, target, state, sha))
    return game, states


def is_header_repaired(path, expected_legacy_hash):
    """Accept only the exact receipt-bound output with VBV 3 changed to 112."""
    try:
        candidate = bytearray(path.read_bytes())
        values = patch_headers(candidate, 3)
        return (set(values) == {VBV_VALUE}
                and hashlib.sha256(candidate).hexdigest() == expected_legacy_hash)
    except (ValueError, IndexError, struct.error):
        return False


def backup_directory(game, binding_hash):
    return safe_path(game / 'saihate-no-ima-movie-backups' / binding_hash[:24])


def validate_backup(backup, binding):
    stored = safe_path(backup / 'binding.json', True)
    if stored.read_bytes() != json_bytes(binding):
        raise ValueError('Backup does not match the exact bundle/render binding')
    for row in binding['targets']:
        checked_hash(backup / 'originals' / row['movie'], row['source_sha256'])


def prepare_backup(backup, binding, states):
    if backup.exists():
        validate_backup(backup, binding)
        return True
    if any(state != 'source' for _, _, state, _ in states):
        raise ValueError('Mixed/already-installed movies require a verified original backup')
    if any(Path(str(target) + TEMP_SUFFIX).exists() for _, target, _, _ in states):
        raise ValueError('Interrupted temporary files without a verified backup; preserved')
    safe_path(backup.parent)
    backup.parent.mkdir(exist_ok=True)
    backup.mkdir()
    exclusive_bytes(backup / 'binding.json', json_bytes(binding))
    (backup / 'originals').mkdir()
    for row, target, _, _ in states:
        copy_exclusive(target, backup / 'originals' / row['movie'], row['source_sha256'])
    validate_backup(backup, binding)
    return False


def quarantine_temporary(temporary, backup):
    temporary = safe_path(temporary)
    if not temporary.exists():
        return 0
    safe_path(temporary, True)
    if temporary.stat().st_size > MAX_MOVIE_BYTES:
        raise ValueError('Interrupted temporary is too large')
    sha = file_hash(temporary)
    folder = safe_path(backup / 'interrupted-temporaries')
    folder.mkdir(exist_ok=True)
    destination = safe_path(folder / (temporary.name + '.' + sha))
    if destination.exists():
        if file_hash(safe_path(destination, True)) != sha:
            raise ValueError('Interrupted recovery destination differs')
        if file_hash(temporary) != sha:
            raise ValueError('Interrupted temporary changed')
        temporary.unlink()
    else:
        temporary.rename(destination)
    return 1


def replace_from(source, target, expected_hash, backup):
    safe_path(target, True)
    writable(target)
    temporary = safe_path(Path(str(target) + TEMP_SUFFIX))
    quarantine_temporary(temporary, backup)
    copy_exclusive(source, temporary, expected_hash)
    os.chmod(temporary, stat.S_IMODE(target.stat().st_mode))
    safe_path(target, True)
    os.replace(temporary, target)
    checked_hash(target, expected_hash)


def mutate(action, game, bundle, renders, developer_qa=False):
    renders, binding, binding_hash = load_binding(bundle, renders, developer_qa, action == 'install')
    game, states = inspect_targets(game, binding)
    backup = backup_directory(game, binding_hash)
    if action == 'restore':
        validate_backup(backup, binding)
        reused = True
    else:
        reused = prepare_backup(backup, binding, states)
    # Revalidate every target and original backup before the first target write.
    _, states = inspect_targets(game, binding)
    validate_backup(backup, binding)
    quarantined = sum(quarantine_temporary(Path(str(target) + TEMP_SUFFIX), backup)
                      for _, target, _, _ in states)
    desired = 'output' if action == 'install' else 'source'
    acceptable = {'output', 'output-repaired'} if action == 'install' else {'source'}
    changes = [(row, target, state, sha) for row, target, state, sha in states if state not in acceptable]
    snapshots = None
    if action == 'restore' and changes:
        # Restore does not require retaining the huge render staging files.
        # Snapshot only changed installed movies so failed restore can roll back.
        transactions = safe_path(backup / 'transactions')
        transactions.mkdir(exist_ok=True)
        snapshots = safe_path(transactions / str(uuid.uuid4()))
        snapshots.mkdir()
        for row, target, _, sha in changes:
            copy_exclusive(target, snapshots / row['movie'], sha)
    attempted = []
    try:
        for row, target, prior_state, prior_hash in changes:
            if file_hash(safe_path(target, True)) != prior_hash:
                raise ValueError('Target changed after transaction preflight')
            previous = (backup / 'originals' / row['movie'] if prior_state == 'source'
                        else snapshots / row['movie'] if snapshots else renders / row['movie'])
            incoming = renders / row['movie'] if action == 'install' else backup / 'originals' / row['movie']
            expected_hash = row['output_sha256'] if action == 'install' else row['source_sha256']
            attempted.append((row, target, previous, prior_hash))
            replace_from(incoming, target, expected_hash, backup)
        _, final_states = inspect_targets(game, binding)
        if any(state not in acceptable for _, _, state, _ in final_states):
            raise RuntimeError('Final all-three movie verification failed')
    except BaseException as failure:
        errors = []
        for row, target, previous, prior_hash in reversed(attempted):
            try:
                replace_from(previous, target, prior_hash, backup)
            except Exception as error:
                errors.append(f'{row["movie"]}: {error}')
        message = ('rollback incomplete: ' + repr(errors) if errors else 'all attempted targets returned to previous exact bytes')
        raise RuntimeError(f'{action} failed; {message}; keep backups at {backup}: {failure}') from failure
    # Delete only successful transaction's owned, exact snapshot files; originals
    # and interrupted partial writes remain recoverable in the retained backup.
    if snapshots:
        for row, _, _, sha in changes:
            checked_hash(snapshots / row['movie'], sha).unlink()
        snapshots.rmdir()
    return {'action': action, 'movie_targets_verified': 3, 'changed_files': len(changes),
            'qa_only': binding['qa_only'], 'backup_retained': str(backup),
            'verified_existing_backup_reused': reused,
            'interrupted_temporary_files_preserved': quarantined, 'game_launched': False}


def repair_installed(game, bundle, renders, developer_qa=False):
    """Repair all installed movies transactionally without changing receipts."""
    _, binding, binding_hash = load_binding(bundle, renders, developer_qa, False)
    game, states = inspect_targets(game, binding)
    if any(state == 'source' for _, _, state, _ in states):
        raise ValueError('Install the optional subtitles before requesting repair')
    backup = backup_directory(game, binding_hash)
    validate_backup(backup, binding)
    transactions = safe_path(backup / 'transactions')
    transactions.mkdir(exist_ok=True)
    snapshots = safe_path(transactions / ('vbv-' + str(uuid.uuid4())))
    snapshots.mkdir()
    changes = []
    for row, target, state, old_hash in states:
        data = bytearray(target.read_bytes())
        if hashlib.sha256(data).hexdigest() != old_hash:
            raise ValueError('Movie changed after repair preflight')
        values = patch_headers(data)
        if not set(values) <= {3, VBV_VALUE}:
            raise ValueError('Unexpected VBV values; movie left untouched')
        new_hash = hashlib.sha256(data).hexdigest()
        if new_hash == old_hash:
            continue
        saved = snapshots / row['movie']
        staged = snapshots / (row['movie'] + '.repaired')
        copy_exclusive(target, saved, old_hash)
        exclusive_bytes(staged, data)
        checked_hash(staged, new_hash, row['output_size'])
        changes.append((row, target, saved, staged, old_hash, new_hash))
    validate_backup(backup, binding)
    for row, target, state, old_hash in states:
        checked_hash(target, old_hash, row['output_size'])
    attempted = []
    try:
        for row, target, saved, staged, old_hash, new_hash in changes:
            checked_hash(target, old_hash, row['output_size'])
            attempted.append((target, saved, old_hash))
            replace_from(staged, target, new_hash, backup)
        _, final = inspect_targets(game, binding)
        if any(state not in {'output', 'output-repaired'} for _, _, state, _ in final):
            raise RuntimeError('Final movie repair verification failed')
    except BaseException as failure:
        errors = []
        for target, saved, old_hash in reversed(attempted):
            try:
                replace_from(saved, target, old_hash, backup)
            except Exception as error:
                errors.append(str(error))
        raise RuntimeError(f'Movie repair failed; rollback errors: {errors}; keep {snapshots}: {failure}') from failure
    for row, target, saved, staged, old_hash, new_hash in changes:
        checked_hash(saved, old_hash).unlink()
        checked_hash(staged, new_hash).unlink()
    snapshots.rmdir()
    return {'action': 'repair', 'movie_targets_verified': 3, 'changed_files': len(changes),
            'backup_retained': str(backup), 'receipt_unchanged': True,
            'picture_audio_and_subtitles_reencoded': False, 'game_launched': False}


def operate(action, game, bundle, renders, developer_qa=False):
    if action not in ('verify', 'install', 'restore', 'repair'):
        raise ValueError('Unknown movie action')
    # Preflight is read-only; mutation happens only after obtaining a shared
    # cooperating-installer lock, then the entire preflight is repeated.
    _, binding, binding_hash = load_binding(bundle, renders, developer_qa, action == 'install')
    game, states = inspect_targets(game, binding)
    backup = backup_directory(game, binding_hash)
    if action == 'verify':
        if backup.exists():
            validate_backup(backup, binding)
        return {'action': action, 'movie_targets_verified': 3,
                'states': {row['movie']: state for row, _, state, _ in states},
                'qa_only': binding['qa_only'], 'game_launched': False}
    lock = safe_path(game / LOCK)
    exclusive_bytes(lock, (binding_hash + '\nmovie-' + action).encode('ascii'))
    lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
    try:
        if action == 'repair':
            return repair_installed(game, bundle, renders, developer_qa)
        return mutate(action, game, bundle, renders, developer_qa)
    finally:
        if lock.exists():
            current = safe_path(lock, True).stat()
            if (current.st_dev, current.st_ino) == lock_identity:
                lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('verify', 'install', 'restore', 'repair'))
    parser.add_argument('game', type=Path)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('renders', type=Path)
    parser.add_argument('--qa-install', '--developer-qa-install', dest='developer_qa_install', action='store_true',
                        help='DEVELOPER ONLY: permit explicitly unapproved QA bundle/receipt; not production approval')
    args = parser.parse_args()
    try:
        result = operate(args.action, args.game, args.bundle, args.renders, args.developer_qa_install)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, StopIteration) as error:
        parser.exit(1, f'Movie operation stopped: {error}\nKeep backups and partial files. Close the game before retrying.\n')


if __name__ == '__main__':
    main()
