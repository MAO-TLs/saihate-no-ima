import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {readerCategories, readerCategoryId} from '../app/reader-categories.mjs';
const index = JSON.parse(readFileSync(new URL('../public/script-data/index.json', import.meta.url)));
test('only story and hyperlinks are browse categories; all image destinations join hyperlinks',()=>{
  const before=JSON.stringify(index);
  const categories=readerCategories(index.routes);
  assert.deepEqual(categories.map(r=>r.id), ['story','hyperlinks']);
  const links=categories[1];
  assert.equal(links.scripts.filter(s=>s.imageOnly).length,10);
  assert.equal(links.scripts.filter(s=>!s.imageOnly).length,147);
  const images=index.routes.find(r=>r.id==='entries');
  for(const script of images.scripts) {
    assert.ok(links.scripts.some(s=>s.routeId==='entries' && s.id===script.id && s.file===script.file));
  }
  assert.equal(new Set(links.scripts.map(s=>`${s.routeId}:${s.id}`)).size,157);
  assert.equal(readerCategoryId('entries'),'hyperlinks');
  assert.equal(readerCategoryId('story'),'story');
  assert.equal(JSON.stringify(index),before,'canonical data and references stay untouched');
});
