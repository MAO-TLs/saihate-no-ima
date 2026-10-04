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
 for(const s of ['SAIHATE','NO&nbsp;IMA','Project Lead','GPT-6 Astra','gambs','v1.0.0/saihate-no-ima-v1.0.0.zip']) assert.ok(page.includes(s));
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
