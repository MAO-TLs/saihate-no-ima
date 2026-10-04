import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, existsSync} from 'node:fs';
import {REPOSITORY_NAME, REPOSITORY_URL, SITE_BASE_PATH, SITE_URL} from '../site-target.mjs';
import {parseReaderLocation, passageHref} from '../app/script/location.mjs';
const read = p => JSON.parse(readFileSync(new URL('../public/script-data/' + p, import.meta.url)));
const index = read('index.json');
const preview = read('hyperlink-entries.json');
const origin = 'https://mao-tls.github.io';
const reader = `${origin}${SITE_BASE_PATH}/script/`;
test('eventual repository and hosted site use the requested saihate-no-ima name', () => {
  assert.equal(REPOSITORY_NAME, 'saihate-no-ima');
  assert.equal(REPOSITORY_URL, 'https://github.com/MAO-TLs/saihate-no-ima');
  assert.equal(SITE_URL, 'https://mao-tls.github.io/saihate-no-ima/');
  assert.match(readFileSync(new URL('../vite.config.ts', import.meta.url), 'utf8'), /base: `\$\{SITE_BASE_PATH\}\//);
});
test('every primary and alternative bilingual hover destination round-trips under the hosted subpath', () => {
  let count = 0;
  for (const route of index.routes) for (const script of route.scripts) for (const row of read(script.file).lines) {
    for (const field of ['hyperlinks', 'japaneseHyperlinks']) for (const link of row[field] ?? []) {
      for (const target of [link, ...(link.alternatives ?? [])]) {
        const href = new URL(passageHref(target.targetRef), reader);
        assert.equal(href.pathname, '/saihate-no-ima/script/');
        assert.equal(href.hash, `#${target.targetRef}`);
        assert.equal(parseReaderLocation(href.href, index).pendingRef, target.targetRef);
        assert.ok(preview.entries[target.targetRef], target.targetRef);
        count++;
      }
    }
  }
  assert.equal(count, 425, 'deduplicated primary/alternative rendered targets across both languages');
});
test('preview images, chapter data, and navigation remain within the repository mount', () => {
  for (const entry of Object.values(preview.entries)) for (const row of entry.lines) for (const image of row.images ?? []) {
    const url = new URL(`..${image.src}`, reader);
    assert.ok(url.pathname.startsWith(`${SITE_BASE_PATH}/`));
    assert.ok(existsSync(new URL('../public' + image.src, import.meta.url)));
  }
  for (const relative of ['../script-data/index.json', '../script-data/hyperlink-entries.json', ...index.routes.flatMap(r => r.scripts.map(s => `../script-data/${s.file}`))]) {
    const url = new URL(relative, reader);
    assert.ok(url.pathname.startsWith(`${SITE_BASE_PATH}/script-data/`));
    assert.ok(existsSync(new URL('../public' + url.pathname.slice(SITE_BASE_PATH.length), import.meta.url)));
  }
  assert.equal(new URL('../', reader).href, SITE_URL);
  assert.equal(new URL('./script/', SITE_URL).href, reader);
  assert.equal(new URL('./forest-hero.png', SITE_URL).pathname, `${SITE_BASE_PATH}/forest-hero.png`);
});
test('hosted subpath history restores exact source query and canonical preview destination', () => {
  const source = `${reader}?scope=all&q=saihate%3Astory%3A0004%3A000232&section=story`;
  const destination = new URL(passageHref('saihate:entries:0004:entry-001230'), source).href;
  const back = parseReaderLocation(source, index);
  assert.equal(back.searchScope, 'corpus');
  assert.equal(back.corpusQuery, 'saihate:story:0004:000232');
  assert.equal(back.corpusRouteId, 'story');
  const forward = parseReaderLocation(destination, index);
  assert.equal(forward.pendingRef, 'saihate:entries:0004:entry-001230');
  assert.equal(forward.routeId, 'entries');
  assert.equal(forward.scriptId, '0004');
  assert.equal(new URL(destination).pathname, '/saihate-no-ima/script/');
});
