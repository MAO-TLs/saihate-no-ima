import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
const read=f=>JSON.parse(readFileSync(new URL('../public/script-data/'+f,import.meta.url)));
const changes=JSON.parse(readFileSync(new URL('./fixtures/v119.json',import.meta.url)));
test('v1.1.9 projects39 approved textual corrections and their search records',()=>{
 const concordance=read('concordance.json').routes.flatMap(r=>r.scripts.flatMap(s=>s.lines));
 assert.equal(changes.filter(c=>c.field==='english').length,39);
 for(const c of changes){
  const row=read(c.ref.split(':')[2]+'.json').lines.find(r=>r.ref===c.ref);
  assert.deepEqual(row[c.field],c.after);
  assert.deepEqual(concordance.find(r=>r[0]===c.ref)[{english:5,hyperlinks:10}[c.field]],c.after);
 }
 assert.equal(read('index.json').version,'1.1.9');
 assert.equal(read('concordance.json').version,'1.1.9');
});
test('v1.1.9 relocated reader hyperlink retains its phrase and destination',()=>{
 const c=changes.find(c=>c.field==='hyperlinks');
 assert.ok(c);
 const row=read(c.ref.split(':')[2]+'.json').lines.find(r=>r.ref===c.ref);
 const oldEnglish=changes.find(x=>x.ref===c.ref&&x.field==='english').before;
 for(let i=0;i<c.after.length;i++){
  const before=c.before[i],after=c.after[i];
  assert.equal(oldEnglish.slice(before.start,before.end),row.english.slice(after.start,after.end));
  assert.equal(before.targetRef,after.targetRef);
 }
});
