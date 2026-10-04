// Run separately after building; these checks bind the actual generated output.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, existsSync} from 'node:fs';
import {SITE_BASE_PATH, SITE_URL} from '../site-target.mjs';
const client = new URL('../dist/client/', import.meta.url);
const pages = [['index.html', SITE_URL], ['script/index.html', `${SITE_URL}script/`]];
test('generated page assets and local navigation resolve within the requested site mount', () => {
  let assets = 0;
  for (const [file, pageUrl] of pages) {
    const html = readFileSync(new URL(file, client), 'utf8');
    assert.doesNotMatch(html, /(?:src|href)="\/(?:assets|script-data|hyperlink-assets)\//);
    for (const [, raw] of html.matchAll(/(?:src|href)="([^"]+)"/g)) {
      if (/^(?:https?:|mailto:|#)/.test(raw)) continue;
      const url = new URL(raw.replaceAll('&amp;', '&'), pageUrl);
      assert.ok(url.pathname.startsWith(`${SITE_BASE_PATH}/`), url.href);
      let path = url.pathname.slice(SITE_BASE_PATH.length + 1);
      if (path.endsWith('/') || !path) path += 'index.html';
      assert.ok(existsSync(new URL(path, client)), `${file}: ${url.href}`);
      if (url.pathname.includes('/assets/')) assets++;
    }
  }
  assert.ok(assets >= 10, assets);
});
test('export contains full source-bound reader data, hover previews and source image assets', () => {
  const source = new URL('../public/script-data/', import.meta.url);
  for (const file of ['index.json','concordance.json','hyperlink-entries.json']) {
    assert.deepEqual(readFileSync(new URL(`script-data/${file}`, client)), readFileSync(new URL(file, source)), file);
  }
  const index = JSON.parse(readFileSync(new URL('index.json', source)));
  for (const route of index.routes) for (const script of route.scripts) {
    assert.deepEqual(readFileSync(new URL(`script-data/${script.file}`, client)), readFileSync(new URL(script.file, source)), script.file);
  }
  const previews = JSON.parse(readFileSync(new URL('hyperlink-entries.json', source)));
  const images = new Set(Object.values(previews.entries).flatMap(e => e.lines.flatMap(r => (r.images ?? []).map(i => i.src))));
  assert.equal(images.size, 10);
  for (const image of images) assert.deepEqual(readFileSync(new URL(image.slice(1), client)), readFileSync(new URL('../public' + image, import.meta.url)), image);
});
