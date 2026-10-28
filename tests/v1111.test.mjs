import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = name => JSON.parse(readFileSync(new URL('../public/script-data/' + name, import.meta.url)));
const ranks = ['Class S', 'Class A+', 'Class A', 'Class B', 'Class C+', 'Class C', 'Class D+', 'Class D'];

test('rank rows and each complete anchor survive in reader, search and previews', () => {
  const row = read('0137.json').lines.find(r => r.sourceId === '0137:000036');
  assert.equal(row.english, ranks.join('\n'));
  assert.equal(row.hyperlinks.length, 8);
  assert.deepEqual(row.hyperlinks.map(link => row.english.slice(link.start, link.end)), ranks);
  const search = read('concordance.json').routes.flatMap(r => r.scripts.flatMap(s => s.lines)).find(r => r[0] === row.ref);
  assert.equal(search[5], row.english);
  assert.deepEqual(search[10], row.hyperlinks);
  const copies = Object.values(read('hyperlink-entries.json').entries).flatMap(e => e.lines).filter(r => r.ref === row.ref);
  assert.ok(copies.length);
  for (const copy of copies) {
    assert.equal(copy.english, row.english);
    assert.deepEqual(copy.hyperlinks, row.hyperlinks);
  }
});

test('the complete English corpus has no ruby markup or reading fields', () => {
  const rows = read('index.json').routes.flatMap(r => r.scripts.flatMap(s => read(s.file).lines));
  const copies = Object.values(read('hyperlink-entries.json').entries).flatMap(e => e.lines);
  const check = (text, label) => assert.doesNotMatch(text || '', /<\/?(?:ruby|rt|rp)\b/i, label);
  assert.equal(rows.length, 46629); // Includes eleven supplemental reader rows.
  for (const row of [...rows, ...copies]) {
    check(row.english, row.ref);
    check(row.speakerEn, row.ref);
    for (const key of Object.keys(row)) {
      if (/english.*(?:ruby|furigana|reading)|(?:ruby|furigana|reading).*english/i.test(key)) {
        assert.ok(!row[key], row.ref + ' ' + key);
      }
    }
  }
  for (const row of read('concordance.json').routes.flatMap(r => r.scripts.flatMap(s => s.lines))) {
    check(row[5], row[0]);
    check(row[3], row[0]);
  }
});
