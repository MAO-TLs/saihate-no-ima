import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {routeLabel} from '../app/route-label.mjs';
test('public category labels do not expose working parity status',()=>{
 assert.equal(routeLabel('Non-text game entries (visual parity pending)'), 'Non-text game entries');
 assert.equal(routeLabel('Main story'), 'Main story');
});
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('canonical MAO publication and reader styles are frozen byte-identical copies',()=>{
 const sha=p=>createHash('sha256').update(read(p)).digest('hex');
 assert.equal(sha('app/mao-publication-template.css'), 'ba5e364b91a96297549ae7c552769af9cff01ae044b15c658e770fd2a55e6d7a');
 assert.equal(sha('app/mao-reader-template.css'), '24728a1a18fa4eec57cc653f3a0911221e07b6fa69368b822789677d739c4b7f');
 const css=read('app/globals.css');
 assert.match(css, /mao-publication-template.css/);
 assert.match(css, /mao-reader-template.css/);
 assert.match(css, /width: min\(1180px, calc\(100% - 48px\)\)/);
});
test('public release copy, repository links and credits are correct',()=>{
 const page=read('app/page.tsx');
 assert.match(page, /<span className="release-label">Version<\/span>\s*<strong>v\d+\.\d+\.\d+<\/strong>/);
 for(const s of ['SAIHATE','NO&nbsp;IMA','Project Lead','GPT-6 Astra','gambs','v1.1.5/saihate-no-ima-v1.1.5.zip']) assert.ok(page.includes(s));
 assert.doesNotMatch(page,/Private preview|Unreleased|in preparation/);
 assert.match(read('app/layout.tsx'),/index: true, follow: true/);
 assert.match(read('app/SiteNav.tsx'),/github.com\/MAO-TLs\/saihate-no-ima/);
 assert.equal(existsSync(new URL('../app/audit',import.meta.url)),false);
 for(const file of ['PRIVATE_RC_FREEZE.json','reader-export-verification.json','evidence']) assert.equal(existsSync(new URL('../'+file,import.meta.url)),false);
});
test('homepage reports bound edition and actual corpus',()=>{
 const page=read('app/page.tsx');
 assert.match(page,/hover-over hyperlinks/);
 assert.match(page,/Saihate no Ima COMPLETE/);
 assert.match(page,/Other editions are not supported/);
 assert.match(page,/countLabel\(index.totalLines, "bilingual passage"\)/);
});
test('download metadata follows the WA2 size, notes, version and compatibility layout',()=>{
 const page=read('app/page.tsx');
 assert.match(page,/Download complete release/);
 assert.match(page,/\d+\.\d MB · <a href="https:\/\/github.com\/MAO-TLs\/saihate-no-ima\/releases\/tag\/v1\.1\.5">Release notes<\/a>/);
 assert.match(page,/Version 1\.1\.5 · Windows \+ Wine · Japanese COMPLETE edition required/);
});
test('reader hides internal categories and implementation warnings without removing image destinations',()=>{
 const browser=read('app/script/ScriptBrowser.tsx');
 assert.match(browser,/const browsableRoutes = readerCategories/);
 assert.match(browser,/browsableRoutes.map\(route => <option/);
 assert.match(browser,/if \(route.id === "entries" \|\| route.id === "system"\) return/);
 assert.match(browser,/!line.images\?\.length && <>/);
 assert.match(browser,/!images\?\.length && <>/);
 assert.match(browser,/routeLabel\(activePayload.routeLabel\)/);
 for (const file of ['app/script/ScriptBrowser.tsx','app/script/HyperlinkPreview.tsx','app/script/page.tsx']) {
  assert.doesNotMatch(read(file),/not emulated|再現していません|<figcaption>/);
 }
 assert.equal(JSON.parse(read('public/script-data/index.json')).version,'1.1.5');
 assert.match(read('app/script/HyperlinkPreview.tsx'),/line.images\?\.map/);
});
