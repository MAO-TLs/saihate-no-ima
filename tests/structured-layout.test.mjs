import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const read = file => JSON.parse(readFileSync(new URL('../public/script-data/'+file,import.meta.url)));
const reviewed = JSON.parse(readFileSync(new URL('./fixtures/structured-layout.json',import.meta.url)));
const rows = read('index.json').routes.flatMap(route=>route.scripts.flatMap(script=>read(script.file).lines));

test('all 52 reviewed structured passages retain boundaries without changing words',()=>{
 assert.equal(reviewed.length,52);
 for(const expected of reviewed) {
  const row=rows.find(row=>row.sourceId===expected.sourceId);
  assert.ok(row,expected.sourceId);
  assert.equal(createHash('sha256').update(row.english.replace(/\s/g,'')).digest('hex'),expected.englishWordHash,row.ref);
  assert.ok(row.english.split('\n').length>=expected.minimumLines,row.ref);
  assert.ok(expected.minimumLines>1,row.ref);
 }
});

test('whole-corpus marked list scan has no remaining collapsed lists',()=>{
 const patterns=[/^\s*[・•]/,/^\s*[□■](?![□■])/,/^\s*[―—]{2,}/,
                 /^\s*[０-９0-9]+[．.]/,/^\s*[→⇒▶▷►▸]/];
 const reviewedIds=new Set(reviewed.map(row=>row.sourceId));
 for(const row of rows) {
  if(patterns.some(pattern=>row.japanese.split('\n').filter(line=>pattern.test(line)).length>1)) {
   assert.ok(reviewedIds.has(row.sourceId),row.ref);
   assert.ok(row.english.includes('\n'),row.ref);
  }
 }
});
