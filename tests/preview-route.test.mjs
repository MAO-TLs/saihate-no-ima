import test from 'node:test';
import assert from 'node:assert/strict';
import {previewRoute} from '../scripts/preview-routing.mjs';
test('local preview mounts exact site path and preserves reader queries on old local aliases', () => {
  assert.deepEqual(previewRoute('/'), {redirect:'/saihate-no-ima/'});
  assert.deepEqual(previewRoute('/saihate-no-ima'), {redirect:'/saihate-no-ima/'});
  assert.deepEqual(previewRoute('/script/?scope=all&q=test'), {redirect:'/saihate-no-ima/script/?scope=all&q=test'});
  assert.deepEqual(previewRoute('/saihate-no-ima/'), {file:'index.html'});
  assert.deepEqual(previewRoute('/saihate-no-ima/script/?scope=all'), {file:'script/index.html'});
  assert.deepEqual(previewRoute('/saihate-no-ima/script-data/index.json'), {file:'script-data/index.json'});
});
test('preview rejects off-mount paths, malformed encoding, and encoded traversal', () => {
  for (const path of ['/other/', '/saihate-no-imax/', '/saihate-no-ima/../../package.json']) assert.deepEqual(previewRoute(path), {status:404});
  for (const path of ['/saihate-no-ima/%E0%A4%A', '/saihate-no-ima/%2e%2e%2fpackage.json', '/saihate-no-ima/%5cpackage.json', '/saihate-no-ima/%2fprivate%2fetc%2fpasswd']) assert.deepEqual(previewRoute(path), {status:400});
});
