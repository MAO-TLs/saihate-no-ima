import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

test('movie header repair, receipt binding, rollback and restoration', () => {
  const result = spawnSync('python3', ['-m', 'unittest', 'movie_install_tests', 'test_movie_vbv'], {
    cwd: new URL('../scripts/movie_tools/', import.meta.url), encoding: 'utf8', timeout: 60000,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  assert.equal(result.status, 0, result.stdout + result.stderr);
});

test('movie-only release retains the script version and credits the contributor', () => {
  const release = readFileSync(new URL('../app/page.tsx', import.meta.url), 'utf8');
  assert.match(release, /releases\/download\/v1\.1\.12\/saihate-no-ima-v1\.1\.12\.zip/);
  assert.match(release, /desidia-cyber/);
  assert.match(release, /scrolling-text twitch is separate/);
  assert.match(readFileSync(new URL('../app/script/page.tsx', import.meta.url), 'utf8'), /Script version v1\.1\.11/);
});
