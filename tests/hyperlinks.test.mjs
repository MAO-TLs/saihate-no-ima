import test from 'node:test';
import assert from 'node:assert/strict';
import { validHyperlinks } from '../app/script/hyperlinks.mjs';
const text = 'one two three';
const link = { start: 4, end: 7, targetRef: '0004:000232', preview: 'Source-bound preview' };
test('toggle hides link metadata without changing text', () => {
  assert.deepEqual(validHyperlinks(text, [link], false), []);
  assert.deepEqual(validHyperlinks(text, [link]), [link]);
  assert.equal(text.slice(0, link.start) + text.slice(link.start, link.end) + text.slice(link.end), text);
});
test('invalid and overlapping ranges are ignored', () => {
  assert.deepEqual(validHyperlinks(text, [null, { ...link, start: -1 }, link, { ...link, start: 5 }, { ...link, end: 99 }, { ...link, targetRef: '' }]), [link]);
});
test('ranges cannot split a Unicode surrogate pair', () => {
  assert.deepEqual(validHyperlinks('A😀B', [{ start: 1, end: 2, targetRef: 'x' }]), []);
  assert.equal(validHyperlinks('A😀B', [{ start: 1, end: 3, targetRef: 'x' }]).length, 1);
});
