import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { validHyperlinks } from '../app/script/hyperlinks.mjs';
const read = p => JSON.parse(readFileSync(new URL('../public/script-data/' + p, import.meta.url)));
const index = read('index.json');
const payloads = index.routes.flatMap(route => route.scripts.map(script => read(script.file)));
const rows = payloads.flatMap(p => p.lines);
const byRef = new Map(rows.map(r => [r.ref, r]));
test('all 46618 bound manuscript records are present once and index counts agree', () => {
  const records = rows.filter(r => r.sourceId);
  assert.equal(records.length, 46618);
  assert.equal(index.totalLines, records.length);
  assert.equal(new Set(records.map(r => r.sourceId)).size, records.length);
  assert.equal(byRef.size, rows.length);
  for (const payload of payloads) assert.equal(payload.lines.length, payload.lineCount);
  for (const row of records) {
    assert.doesNotMatch(row.english, /<\/?h>|Translation withheld under policy/);
    assert.equal(typeof row.japanese, 'string');
  }
});
test('every rendered hyperlink range and destination is valid, including alternate entries', () => {
  let links = 0;
  for (const row of rows) {
    const valid = validHyperlinks(row.english, row.hyperlinks);
    assert.equal(valid.length, row.hyperlinks.length, row.ref);
    for (const link of valid) {
      assert.ok(byRef.has(link.targetRef), `${row.ref} → ${link.targetRef}`);
      links++;
      for (const alternate of link.alternatives ?? []) {
        assert.ok(byRef.has(alternate.targetRef));
        links++;
      }
    }
    const japanese = validHyperlinks(row.japanese, row.japaneseHyperlinks);
    assert.equal(japanese.length, row.japaneseHyperlinks?.length ?? 0);
    assert.deepEqual([...new Set(japanese.flatMap(h => [h.targetRef, ...(h.alternatives ?? []).map(a => a.targetRef)]))].sort(), [...new Set(valid.flatMap(h => [h.targetRef, ...(h.alternatives ?? []).map(a => a.targetRef)]))].sort(), row.ref);
  }
  assert.ok(links >= 200);
});
test('corpus search data is byte-equivalent to the chapter payloads', () => {
  const concordance = read('concordance.json');
  assert.equal(concordance.totalLines, index.totalLines);
  const compactRows = concordance.routes.flatMap(r => r.scripts.flatMap(s => s.lines));
  assert.equal(compactRows.length, rows.length);
  for (const r of compactRows) {
    const original = byRef.get(r[0]);
    assert.equal(r[4], original.japanese);
    assert.equal(r[5], original.english);
    assert.deepEqual(r[10], original.hyperlinks);
    assert.deepEqual(r[11], original.japaneseHyperlinks ?? []);
    assert.deepEqual(r[12], original.images ?? []);
  }
});
test('accepted bilingual hyperlink targets remain equivalent in all 193 linked source records', () => {
  const targets = links => [...new Set(links.flatMap(h => [h.targetRef, ...(h.alternatives ?? []).map(a => a.targetRef)]))].sort();
  const linked = rows.filter(row => row.hyperlinks.length);
  assert.equal(linked.length, 193);
  for (const row of linked) {
    assert.deepEqual(targets(row.hyperlinks), targets(row.japaneseHyperlinks), row.ref);
    assert.equal(validHyperlinks(row.japanese, row.japaneseHyperlinks).length, row.japaneseHyperlinks.length);
  }
});
test('non-text destinations are explicitly marked incomplete, never fabricated translation', () => {
  const entries = rows.filter(r => r.entryKind === 'nontext');
  assert.equal(entries.length, 11);
  for (const entry of entries) {
    assert.equal(entry.japanese, '');
    assert.match(entry.english, /not emulated/);
    assert.ok(entry.images.length > 0);
    for (const image of entry.images) {
      const bytes = readFileSync(new URL('../public' + image.src, import.meta.url));
      assert.equal(createHash('sha256').update(bytes).digest('hex'), image.pngSha256);
    }
    assert.ok(Number.isInteger(entry.entryInstruction));
  }
});
test('hover cards cover every bilingual destination with exact full source-bound passages and images', () => {
  const previews = read('hyperlink-entries.json');
  assert.equal(previews.schema, 'saihate-hyperlink-previews/1');
  const targets = new Set(rows.flatMap(row => [...row.hyperlinks, ...(row.japaneseHyperlinks ?? [])].flatMap(h => [h.targetRef, ...(h.alternatives ?? []).map(a => a.targetRef)])));
  assert.deepEqual(Object.keys(previews.entries).sort(), [...targets].sort());
  for (const [ref, entry] of Object.entries(previews.entries)) {
    assert.equal(entry.targetRef, ref);
    assert.equal(entry.lines[0].ref, ref);
    assert.ok(entry.lines.length > 0);
    for (const row of entry.lines) assert.deepEqual(row, byRef.get(row.ref), ref);
  }
  assert.ok(previews.entries['saihate:story:0009:000011'].lines.length > 1, 'passages are not first-line tooltips');
  assert.equal(previews.entries['saihate:entries:0004:entry-001230'].lines[0].images[0].graphicId, 458);
});
