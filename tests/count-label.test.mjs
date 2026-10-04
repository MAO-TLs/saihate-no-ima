import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {countLabel} from '../app/count-label.mjs';
test('reader counts use singular for exactly one and plural for zero or many', () => {
  assert.equal(countLabel(1, 'line'), '1 line');
  assert.equal(countLabel(1, 'source line'), '1 source line');
  assert.equal(countLabel(1, 'script'), '1 script');
  assert.equal(countLabel(0, 'line'), '0 lines');
  assert.equal(countLabel(2, 'source line'), '2 source lines');
  assert.equal(countLabel(46618, 'line'), '46,618 lines');
});
test('reader option and source count labels use the shared formatter, and corpus prompt names this game', () => {
  const browser = readFileSync(new URL('../app/script/ScriptBrowser.tsx', import.meta.url), 'utf8');
  assert.match(browser, /countLabel\(script.lineCount, "line"\)/);
  assert.match(browser, /countLabel\(activePayload.lineCount, "source line"\)/);
  assert.match(browser, /<code>saihate:<\/code> reference/);
  assert.doesNotMatch(browser, /<code>wa2:|<code>wa2mas:|in the main game and Special Contents/);
});
