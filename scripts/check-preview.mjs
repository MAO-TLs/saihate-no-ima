// Read-only HTTP smoke check of the running local preview, not a browser UI test.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {SITE_BASE_PATH} from '../site-target.mjs';
const origin = 'http://127.0.0.1:4322';
const base = `${origin}${SITE_BASE_PATH}/`;
const publicDir = new URL('../public/', import.meta.url);
const digest = data => createHash('sha256').update(data).digest('hex');
let pages = 0, assets = new Set(), payloads = 0, images = new Set();
for (const path of ['', 'script/']) {
  const response = await fetch(base + path);
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type'), /text\/html/);
  const html = await response.text();
  for (const [, raw] of html.matchAll(/(?:src|href)="([^"]+)"/g)) {
    const url = new URL(raw.replaceAll('&amp;', '&'), base + path);
    if (url.origin === origin && url.pathname.includes('/assets/')) assets.add(url.href);
  }
  pages++;
}
for (const url of assets) {
  assert.ok(new URL(url).pathname.startsWith(`${SITE_BASE_PATH}/assets/`));
  const response = await fetch(url);
  assert.equal(response.status, 200, url);
  assert.match(response.headers.get('content-type'), /text\/(javascript|css)/);
}
const index = JSON.parse(readFileSync(new URL('script-data/index.json', publicDir)));
const files = ['index.json', 'concordance.json', 'hyperlink-entries.json', ...index.routes.flatMap(r => r.scripts.map(s => s.file))];
for (const file of files) {
  const response = await fetch(`${base}script-data/${file}`);
  assert.equal(response.status, 200, file);
  assert.match(response.headers.get('content-type'), /application\/json/);
  assert.equal(digest(Buffer.from(await response.arrayBuffer())), digest(readFileSync(new URL(`script-data/${file}`, publicDir))), file);
  payloads++;
}
const preview = JSON.parse(readFileSync(new URL('script-data/hyperlink-entries.json', publicDir)));
for (const entry of Object.values(preview.entries)) for (const row of entry.lines) for (const image of row.images ?? []) images.add(image.src);
for (const image of images) {
  const response = await fetch(base + image.slice(1));
  assert.equal(response.status, 200, image);
  assert.match(response.headers.get('content-type'), /image\/png/);
  assert.equal(digest(Buffer.from(await response.arrayBuffer())), digest(readFileSync(new URL(image.slice(1), publicDir))), image);
}
for (const [path, location] of [['/', `${SITE_BASE_PATH}/`], ['/script/?scope=all&q=saihate%3Astory%3A0004%3A000232', `${SITE_BASE_PATH}/script/?scope=all&q=saihate%3Astory%3A0004%3A000232`]]) {
  const response = await fetch(origin + path, {redirect:'manual'});
  assert.equal(response.status, 302);
  assert.equal(response.headers.get('location'), location);
}
assert.equal((await fetch(`${origin}/other/`)).status, 404);
assert.equal((await fetch(`${base}%2e%2e%2fpackage.json`)).status, 400);
console.log(JSON.stringify({pages, assetBundles:assets.size, exactReaderPayloads:payloads, exactSourceImages:images.size, aliasRedirects:2, offMountAndTraversalRejected:true, browserUiTest:false}));
