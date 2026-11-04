"""Prepare a tiny source-required movie subtitle bundle, never install a movie.

Production requires exact, affirmative editorial approval for every draft.
--qa permits clearly marked, unapproved local rendering only.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

SCHEMA = 'saihate-source-required-movie-subtitles-v1'
APPROVAL_KEYS = {'source_sha256', 'cue_manifest_sha256', 'subtitle_track_sha256',
                 'reviewer', 'caption_review_complete', 'sampled_subtitle_pacing_review_complete',
                 'bottom_center_presentation_approved', 'approved_for_source_required_rendering',
                 'review_scope'}
REVIEW_SCOPE_KEYS = {'method', 'included_cue_count', 'changed_cues_visually_rechecked',
                     'pacing_sample_ranges_seconds', 'exhaustive_timing_review'}
SUPPORTED = (
    ('b8866d3b8b25c999f6ba09da9eef5cf211ddecaf8d1e7e4d5f96338d2e5674c9', 7441,
     'ba60198f64a49f6ae362b7a8151b5e0dd0df0bb02277e610ca380276d07769e2'),
    ('666a3591cb9613e35aa6fd518b3e542e67e8d5d27d700b70a6bc494c6c8a8b2c', 7490,
     'd8c6ce5252a394c326708fd61a013d251e3bc2abe0398cee8bf14d4ba5ec11a8'),
    ('348eb8bae104a12c28043d31d906ec5b4b69e380ee0192dfc7680c080d610522', 7490,
     'd8c6ce5252a394c326708fd61a013d251e3bc2abe0398cee8bf14d4ba5ec11a8'),
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def manifest_fingerprint(manifest):
    return digest(json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':')).encode('utf-8'))


def compile_ass(manifest, preview_range=None):
    # Building requires the existing project compiler. Rendering an already
    # prepared bundle needs only movie_render.py and this companion module;
    # do not impose a hidden project-tree dependency on the recipient.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from movie_subtitles import compile_ass as compiler
    return compiler(manifest, preview_range)


def file_hash(path):
    result = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def regular_file(path):
    path = Path(path).absolute()
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError(f'Expected a regular, unlinked input file: {path}')
    if any(parent.is_symlink() for parent in path.parents):
        raise ValueError(f'Linked parent directory is not supported: {path}')
    return path


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def approval_binding(draft, track):
    return {'source_sha256': draft['source_sha256'],
            'cue_manifest_sha256': manifest_fingerprint(draft),
            'subtitle_track_sha256': digest(track)}


def subtitle_cue_count(track):
    text = track.decode('utf-8') if isinstance(track, bytes) else track
    return sum(line.startswith('Dialogue:') for line in text.splitlines())


def validate_review_scope(scope, cue_count, duration_seconds):
    """Bound the recorded sample claim; never imply exhaustive viewing.

    Export-only metadata checks pass cue_count=None; callers with a bound ASS
    track must additionally provide its actual Dialogue count.
    """
    if not isinstance(scope, dict) or set(scope) != REVIEW_SCOPE_KEYS:
        raise ValueError('Unexpected sampled review scope fields')
    if (scope['method'] != 'focused-motion-and-still-samples'
            or type(scope['included_cue_count']) is not int or scope['included_cue_count'] <= 0
            or (cue_count is not None and scope['included_cue_count'] != cue_count)
            or scope['changed_cues_visually_rechecked'] is not True
            or scope['exhaustive_timing_review'] is not False):
        raise ValueError('Sampled review method/count/boolean scope differs')
    ranges = scope['pacing_sample_ranges_seconds']
    if not isinstance(ranges, list) or not ranges:
        raise ValueError('Sampled pacing review needs explicit nonempty ranges')
    if type(duration_seconds) not in (int, float) or not math.isfinite(duration_seconds) or duration_seconds <= 0:
        raise ValueError('Invalid bound movie duration')
    previous_end = 0
    for interval in ranges:
        if (not isinstance(interval, list) or len(interval) != 2
                or any(type(value) not in (int, float) or not 0 <= value <= duration_seconds
                       or not math.isfinite(value) for value in interval)):
            raise ValueError('Pacing sample ranges must contain two finite numeric seconds')
        start, end = interval
        if not 0 <= previous_end <= start < end <= duration_seconds:
            raise ValueError('Pacing ranges must ascend without overlap within the movie duration')
        previous_end = end


def validate_approval_fields(approval, expected_binding, track, duration_seconds):
    if not isinstance(approval, dict) or set(approval) != APPROVAL_KEYS:
        raise ValueError('Exact editorial approval is required')
    if any(approval.get(key) is not True for key in (
            'caption_review_complete', 'sampled_subtitle_pacing_review_complete',
            'bottom_center_presentation_approved', 'approved_for_source_required_rendering')):
        raise ValueError('All four editorial approval fields must explicitly be true')
    if any(approval.get(key) != value for key, value in expected_binding.items()):
        raise ValueError('Editorial approval does not bind this exact source/draft/track')
    if not isinstance(approval.get('reviewer'), str) or not approval['reviewer'].strip():
        raise ValueError('Editorial approval needs an identified reviewer')
    validate_review_scope(approval['review_scope'], subtitle_cue_count(track), duration_seconds)


def validate_approval(draft, track, approval, duration_seconds):
    if draft.get('caption_review_complete') is not True:
        raise ValueError('Included-caption source/content review is not complete; production is refused')
    validate_approval_fields(approval, approval_binding(draft, track), track, duration_seconds)


def build_bundle(drafts_dir, output, approval_path=None, qa=False):
    drafts_dir, output = Path(drafts_dir), Path(output).absolute()
    if os.path.lexists(output):
        raise FileExistsError('Choose a new bundle directory; existing data is preserved')
    if any(parent.is_symlink() for parent in output.parents):
        raise ValueError('Linked output directory is not supported')
    approvals = {}
    if approval_path:
        approvals = json.loads(regular_file(approval_path).read_text(encoding='utf-8'))
    if qa and approval_path:
        raise ValueError('QA bundles cannot present production approval')
    entries, files = [], {}
    # Complete all editorial checks before creating any output directory.
    for number, (source_hash, frames, audio_hash) in enumerate(SUPPORTED):
        draft = json.loads(regular_file(drafts_dir / f'movie-{number:02d}-cues-draft.json').read_text(encoding='utf-8'))
        if draft['source_sha256'] != source_hash:
            raise ValueError('Draft source differs from the supported COMPLETE movie')
        track = compile_ass(draft, (0, draft['duration_seconds']) if qa else None).encode('utf-8')
        movie = f'mv{number:04d}.bin'
        approval = approvals.get(movie)
        if not qa:
            # Decoded frame count is authoritative; MPEG container duration
            # estimates differ slightly between supported stream variants.
            validate_approval(draft, track, approval, frames / 30)
        track_name = f'movie-{number:02d}.ass'
        files[track_name] = track
        entries.append({'movie': movie, 'source_path': f'HD/{movie}',
                        'subtitle_track': track_name,
                        **approval_binding(draft, track),
                        'expected_video_frames': frames,
                        'expected_audio_packet_sha256': audio_hash,
                        'editorial_approval': approval if not qa else None})
    manifest = {'schema': SCHEMA, 'qa_only': qa, 'installed': False,
                'contains_game_media': False, 'movies': entries,
                'prerequisites': ['Python 3.10+', 'FFmpeg 5.1+ and matching ffprobe with libass',
                                  'Arial font available to libass'],
                'reproducibility': 'Exact output only for the same FFmpeg/libass/font environment; output SHA-256 is recorded, not asserted across platforms.'}
    output.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        with (output / name).open('xb') as target:
            target.write(data)
    with (output / 'movie-bundle.json').open('xb') as target:
        target.write(json_bytes(manifest))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('drafts_dir', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--approval', type=Path)
    parser.add_argument('--qa', action='store_true')
    args = parser.parse_args()
    result = build_bundle(args.drafts_dir, args.output, args.approval, args.qa)
    print(json.dumps({'bundle': str(args.output), 'movies': len(result['movies']),
                      'qa_only': result['qa_only'], 'installed': False,
                      'media_payload_bytes': 0}))


if __name__ == '__main__':
    main()
