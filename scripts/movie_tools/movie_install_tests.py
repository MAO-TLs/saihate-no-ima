"""Bounded fictional-byte movie installation fixtures; never touch the game."""
import copy
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import movie_bundle as bundle_tools
import movie_render as render_tools
import movie_install as installer


class MovieInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='saihate-movie-install-fixture-')
        self.root = Path(self.temp.name).resolve()
        self.game, self.bundle, self.renders = [self.root / name for name in ('game', 'bundle', 'renders')]
        (self.game / 'HD').mkdir(parents=True)
        self.renders.mkdir()
        self.sources = [f'FICTIONAL ORIGINAL {n}'.encode() for n in range(3)]
        self.outputs = [f'FICTIONAL SUBTITLED {n}'.encode() for n in range(3)]
        self.specs = tuple((bundle_tools.digest(data), 90, 'a' * 64) for data in self.sources)
        self.patchers = [patch.object(module, 'SUPPORTED', self.specs) for module in (bundle_tools, render_tools)]
        for patcher in self.patchers:
            patcher.start()
        drafts = self.root / 'drafts'
        drafts.mkdir()
        for n, data in enumerate(self.sources):
            (self.game / 'HD' / f'mv{n:04d}.bin').write_bytes(data)
            (self.renders / f'mv{n:04d}.bin').write_bytes(self.outputs[n])
            draft = {'source_sha256': self.specs[n][0], 'duration_seconds': 3,
                     'caption_review_complete': False, 'cues': [{'start': .1, 'end': 2,
                     'english': 'Fictional fixture caption.', 'source_binding': 'fictional', 'timing_reviewed': True}]}
            (drafts / f'movie-{n:02d}-cues-draft.json').write_bytes(bundle_tools.json_bytes(draft))
        manifest = bundle_tools.build_bundle(drafts, self.bundle, qa=True)
        self.receipt = {'schema': 'saihate-movie-render-receipt-v1', 'qa_only': True,
            'installed': False, 'render_complete': True,
            'bundle_sha256': bundle_tools.file_hash(self.bundle / 'movie-bundle.json'), 'movies': []}
        for n, entry in enumerate(manifest['movies']):
            self.receipt['movies'].append({'movie': entry['movie'], 'source_sha256': self.specs[n][0],
                'subtitle_track_sha256': entry['subtitle_track_sha256'],
                'sha256': bundle_tools.digest(self.outputs[n]), 'size_bytes': len(self.outputs[n]),
                'video_frames': 90, 'audio_packet_sha256': 'a' * 64,
                'video_start_seconds': '.533333', 'audio_start_seconds': '.533333',
                'full_decode_passed': True, 'font_selection': ['fontselect: (Arial, 400, 0) -> ArialMT, 0, ArialMT']})
        self.write_receipt()
        self.sentinels = {'save.dat': b'KEEP SAVE', 'settings.dat': b'KEEP SETTINGS',
                          'HD/other.bin': b'KEEP OTHER GAME MEDIA'}
        for name, data in self.sentinels.items():
            (self.game / name).write_bytes(data)

    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
        self.temp.cleanup()

    def write_receipt(self):
        (self.renders / 'movie-render-receipt.json').write_bytes(bundle_tools.json_bytes(self.receipt))

    def action(self, action, qa=True):
        return installer.operate(action, self.game, self.bundle, self.renders, qa)

    def movie_bytes(self):
        return [(self.game / 'HD' / f'mv{n:04d}.bin').read_bytes() for n in range(3)]

    def assert_sentinels(self):
        for name, data in self.sentinels.items():
            self.assertEqual((self.game / name).read_bytes(), data)
        self.assertFalse((self.game / installer.LOCK).exists())

    def test_install_restore_reinstall_and_exact_original_backup(self):
        first = self.action('install')
        self.assertEqual(self.movie_bytes(), self.outputs)
        backup = Path(first['backup_retained'])
        self.assertEqual([(backup / 'originals' / f'mv{n:04d}.bin').read_bytes() for n in range(3)], self.sources)
        self.assertEqual(self.action('verify')['states'], {f'mv{n:04d}.bin': 'output' for n in range(3)})
        self.action('restore')
        self.assertEqual(self.movie_bytes(), self.sources)
        repeat = self.action('install')
        self.assertTrue(repeat['verified_existing_backup_reused'])
        self.assertEqual(self.movie_bytes(), self.outputs)
        self.assert_sentinels()

    def test_qa_rejected_without_developer_opt_in(self):
        with self.assertRaises(ValueError):
            self.action('install', False)
        self.assertEqual(self.movie_bytes(), self.sources)
        self.assertFalse((self.game / 'saihate-no-ima-movie-backups').exists())

    def test_exact_production_bundle_and_receipt(self):
        manifest_path = self.bundle / 'movie-bundle.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['qa_only'] = False
        for entry in manifest['movies']:
            entry['editorial_approval'] = {key: entry[key] for key in
                ('source_sha256', 'cue_manifest_sha256', 'subtitle_track_sha256')}
            entry['editorial_approval'].update({'caption_review_complete': True,
                'sampled_subtitle_pacing_review_complete': True, 'bottom_center_presentation_approved': True,
                'approved_for_source_required_rendering': True, 'reviewer': 'Fictional fixture reviewer',
                'review_scope': {'method': 'focused-motion-and-still-samples', 'included_cue_count': 1,
                                 'changed_cues_visually_rechecked': True,
                                 'pacing_sample_ranges_seconds': [[.1, 2]], 'exhaustive_timing_review': False}})
        manifest_path.write_bytes(bundle_tools.json_bytes(manifest))
        self.receipt['qa_only'] = False
        self.receipt['bundle_sha256'] = bundle_tools.file_hash(manifest_path)
        self.write_receipt()
        self.action('install', False)
        self.assertEqual(self.movie_bytes(), self.outputs)
        self.action('restore', False)
        self.assertEqual(self.movie_bytes(), self.sources)

    def test_mixed_interrupted_install_resume_and_partial_preservation(self):
        first = self.action('install')
        (self.game / 'HD/mv0001.bin').write_bytes(self.sources[1])
        partial = self.game / ('HD/mv0001.bin' + installer.TEMP_SUFFIX)
        partial.write_bytes(b'PRESERVE INTERRUPTED PARTIAL')
        resumed = self.action('install')
        self.assertEqual(resumed['changed_files'], 1)
        self.assertEqual(resumed['interrupted_temporary_files_preserved'], 1)
        self.assertEqual(self.movie_bytes(), self.outputs)
        preserved = list((Path(first['backup_retained']) / 'interrupted-temporaries').iterdir())
        self.assertEqual(preserved[0].read_bytes(), b'PRESERVE INTERRUPTED PARTIAL')
        self.assert_sentinels()

    def test_mixed_restore_preserves_partial(self):
        first = self.action('install')
        (self.game / 'HD/mv0000.bin').write_bytes(self.sources[0])
        partial = self.game / ('HD/mv0002.bin' + installer.TEMP_SUFFIX)
        partial.write_bytes(b'PARTIAL TO RETAIN')
        restored = self.action('restore')
        self.assertEqual(restored['changed_files'], 2)
        self.assertEqual(self.movie_bytes(), self.sources)
        self.assertEqual(next((Path(first['backup_retained']) / 'interrupted-temporaries').iterdir()).read_bytes(), b'PARTIAL TO RETAIN')

    def test_install_failure_after_replacement_rolls_back_all_attempted_targets(self):
        original = installer.replace_from
        calls = 0
        def fail_once(*args):
            nonlocal calls
            calls += 1
            original(*args)
            if calls == 2:
                raise OSError('fictional failure after atomic replacement')
        with patch.object(installer, 'replace_from', side_effect=fail_once):
            with self.assertRaisesRegex(RuntimeError, 'previous exact bytes'):
                self.action('install')
        self.assertEqual(self.movie_bytes(), self.sources)
        self.assert_sentinels()
        self.action('install')
        self.assertEqual(self.movie_bytes(), self.outputs)

    def test_restore_failure_rolls_back_exact_prior_mixed_state(self):
        self.action('install')
        (self.game / 'HD/mv0000.bin').write_bytes(self.sources[0])
        before = self.movie_bytes()
        original = installer.replace_from
        calls = 0
        def fail_once(*args):
            nonlocal calls
            calls += 1
            original(*args)
            if calls == 2:
                raise OSError('fictional restore failure')
        with patch.object(installer, 'replace_from', side_effect=fail_once):
            with self.assertRaisesRegex(RuntimeError, 'previous exact bytes'):
                self.action('restore')
        self.assertEqual(self.movie_bytes(), before)
        self.assert_sentinels()
        self.action('restore')
        self.assertEqual(self.movie_bytes(), self.sources)

    def test_incomplete_rollback_retains_recoverable_originals(self):
        original = installer.replace_from
        calls = 0
        def fail_then_rollback_fails(*args):
            nonlocal calls
            calls += 1
            if calls == 1:
                original(*args)
            raise OSError('fictional rollback failure')
        with patch.object(installer, 'replace_from', side_effect=fail_then_rollback_fails):
            with self.assertRaisesRegex(RuntimeError, 'rollback incomplete'):
                self.action('install')
        self.action('restore')
        self.assertEqual(self.movie_bytes(), self.sources)
        self.assert_sentinels()

    def test_restore_after_staged_movie_files_removed(self):
        self.action('install')
        for n in range(3):
            (self.renders / f'mv{n:04d}.bin').unlink()
        self.action('restore')
        self.assertEqual(self.movie_bytes(), self.sources)
        self.assert_sentinels()

    def test_wrong_edition_or_render_tamper_before_mutation(self):
        (self.game / 'HD/mv0001.bin').write_bytes(b'UNKNOWN USER MOVIE')
        before = self.movie_bytes()
        with self.assertRaises(ValueError):
            self.action('install')
        self.assertEqual(self.movie_bytes(), before)
        self.assertFalse((self.game / 'saihate-no-ima-movie-backups').exists())
        (self.game / 'HD/mv0001.bin').write_bytes(self.sources[1])
        (self.renders / 'mv0002.bin').write_bytes(b'TAMPERED OUTPUT')
        with self.assertRaises(ValueError):
            self.action('install')
        self.assertEqual(self.movie_bytes(), self.sources)

    def test_invalid_receipt_modes_and_technical_bindings(self):
        original = copy.deepcopy(self.receipt)
        changes = [('render_complete', 'true'), ('qa_only', False), ('bundle_sha256', '0' * 64)]
        for key, value in changes:
            self.receipt = copy.deepcopy(original)
            self.receipt[key] = value
            self.write_receipt()
            with self.assertRaises(ValueError):
                self.action('install')
        for key, value in [('movie', '../save.dat'), ('video_frames', 1), ('audio_packet_sha256', 'b' * 64),
                           ('full_decode_passed', 'true'), ('audio_start_seconds', 'nan'), ('font_selection', [])]:
            self.receipt = copy.deepcopy(original)
            self.receipt['movies'][0][key] = value
            self.write_receipt()
            with self.assertRaises(ValueError):
                self.action('install')
        self.assertEqual(self.movie_bytes(), self.sources)

    def test_symlink_hardlink_and_parent_alias_refusal(self):
        target = self.game / 'HD/mv0000.bin'
        owned = self.root / 'owned.bin'
        target.rename(owned)
        target.symlink_to(owned)
        with self.assertRaises(ValueError):
            self.action('install')
        target.unlink()
        os.link(owned, target)
        with self.assertRaises(ValueError):
            self.action('install')
        target.unlink()
        owned.rename(target)
        alias = self.root / 'game-alias'
        alias.symlink_to(self.game, target_is_directory=True)
        with self.assertRaises(ValueError):
            installer.operate('install', alias, self.bundle, self.renders, True)
        self.assertEqual(self.movie_bytes(), self.sources)

    def test_posix_and_windows_readonly_refusal_without_permission_changes(self):
        target = self.game / 'HD/mv0001.bin'
        target.chmod(0o444)
        with self.assertRaises(ValueError):
            self.action('install')
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o444)
        target.chmod(0o600)
        with patch.object(Path, 'stat', return_value=SimpleNamespace(st_mode=stat.S_IFREG | 0o600, st_file_attributes=1)):
            with self.assertRaises(ValueError):
                installer.writable(target)
        with patch.object(Path, 'lstat', return_value=SimpleNamespace(st_mode=stat.S_IFDIR | 0o700, st_file_attributes=0x400)):
            with self.assertRaises(ValueError):
                installer.safe_path(target)
        self.assertEqual(self.movie_bytes(), self.sources)

    def test_bad_backup_stale_lock_and_partial_without_backup_preserved(self):
        partial = self.game / ('HD/mv0000.bin' + installer.TEMP_SUFFIX)
        partial.write_bytes(b'UNOWNED PARTIAL')
        with self.assertRaises(ValueError):
            self.action('install')
        self.assertEqual(partial.read_bytes(), b'UNOWNED PARTIAL')
        partial.unlink()
        lock = self.game / installer.LOCK
        lock.write_bytes(b'ANOTHER LIVE OR STALE INSTALLER')
        with self.assertRaises(FileExistsError):
            self.action('install')
        self.assertEqual(lock.read_bytes(), b'ANOTHER LIVE OR STALE INSTALLER')
        lock.unlink()
        installed = self.action('install')
        backup = Path(installed['backup_retained'])
        (backup / 'originals/mv0001.bin').write_bytes(b'CORRUPT ORIGINAL BACKUP')
        before = self.movie_bytes()
        with self.assertRaises(ValueError):
            self.action('restore')
        self.assertEqual(self.movie_bytes(), before)

    def test_duplicate_json_refused(self):
        (self.renders / 'movie-render-receipt.json').write_text('{"qa_only":true,"qa_only":false}')
        with self.assertRaises(ValueError):
            self.action('install')
        self.assertEqual(self.movie_bytes(), self.sources)

    def test_installer_standalone_with_packaged_companions(self):
        isolated = self.root / 'isolated-tools'
        isolated.mkdir()
        for name in ('movie_install.py', 'movie_render.py', 'movie_bundle.py', 'movie_mpeg.py', 'fix_movie_vbv.py'):
            shutil.copyfile(Path(__file__).resolve().parent / name, isolated / name)
        result = subprocess.run([sys.executable, str(isolated / 'movie_install.py'), '--help'],
                                cwd=isolated, capture_output=True, text=True, check=True)
        self.assertIn('--qa-install', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
