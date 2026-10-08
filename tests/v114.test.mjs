import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {test} from 'node:test';
import {scriptDataHref} from '../app/script/reader-data.mjs';
const read = name => JSON.parse(readFileSync(new URL('../public/script-data/' + name, import.meta.url)));
// JSON-stringified v1.1.3 payloads pinned from the published 2a08b5a commit.
const hash = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
const ref = 'saihate:story:0008:004636';

test('v1.1.4 changes exactly the approved English field, preserving Japanese and links', () => {
  const current = read('0008.json');
  const line = current.lines.find(r => r.ref === ref);
  assert.equal(line.english, '(I… ‘I’… know this…?)');
  line.english = '(I… no, I… know this…?)';
  assert.equal(hash(current), 'd36edfec572dbd1e68d5bf1199b698b2e23fdf889fbd89b86c4f65814d83a2f9');
});

test('v1.1.4 search corpus carries the same single correction', () => {
  const current = read('concordance.json');
  let count = 0;
  for (const route of current.routes) for (const script of route.scripts) for (const row of script.lines) {
    if (row[0] === ref) {
      assert.equal(row[5], '(I… ‘I’… know this…?)');
      row[5] = '(I… no, I… know this…?)';
      count++;
    }
  }
  assert.equal(count, 1);
  assert.equal(current.version, '1.1.4');
  current.version = 'private-20261004';
  assert.equal(hash(current), '538927fbc69054d163139bd218fd18ae5172a27e7bff466dc673fa39e8ab6324');
});

test('v1.1.4 reader metadata and cache revision match', () => {
  assert.equal(read('index.json').version, '1.1.4');
  assert.equal(new URL(scriptDataHref('0008.json'), 'https://example.com/script/').searchParams.get('rev'),
    'v1.1.4-20261008-78fee6aed03d');
});
