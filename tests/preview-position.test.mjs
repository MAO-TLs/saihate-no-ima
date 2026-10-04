import test from 'node:test';
import assert from 'node:assert/strict';
import {previewPosition} from '../app/script/preview-position.mjs';
test('preview sits above the trigger when it fits', () => {
  assert.deepEqual(previewPosition({left: 100, top: 500, bottom: 530}, {width: 1200, height: 800}, {height: 300}), {left: 100, top: 190, width: 380, maxHeight: 300});
});
test('preview flips below a top-edge trigger and clamps at right edge', () => {
  const p = previewPosition({left: 1190, top: 50, bottom: 80}, {width: 1200, height: 800}, {height: 500});
  assert.deepEqual(p, {left: 808, top: 90, width: 380, maxHeight: 360});
});
test('long passage card fits narrow and short viewports', () => {
  const p = previewPosition({left: 310, top: 200, bottom: 220}, {width: 320, height: 300}, {height: 1000});
  assert.equal(p.left, 12);
  assert.equal(p.width, 296);
  assert.ok(p.top + p.maxHeight <= 288);
});
test('mobile-width image and long-passage cards remain within all viewport edges', () => {
  for (const viewport of [{width:320,height:568}, {width:390,height:844}, {width:640,height:360}]) {
    for (const rect of [
      {left:0,top:0,bottom:24},
      {left:viewport.width - 20,top:40,bottom:64},
      {left:viewport.width / 2,top:viewport.height - 30,bottom:viewport.height - 6},
    ]) for (const height of [160, 300, 10000]) {
      const p = previewPosition(rect, viewport, {height});
      assert.ok(p.left >= 12);
      assert.ok(p.top >= 12);
      assert.ok(p.left + p.width <= viewport.width - 12);
      assert.ok(p.top + p.maxHeight <= viewport.height - 12);
    }
  }
});
