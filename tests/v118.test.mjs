import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
const read=f=>JSON.parse(readFileSync(new URL('../public/script-data/'+f,import.meta.url)));
const changes=JSON.parse(readFileSync(new URL('./fixtures/v118.json',import.meta.url)));
test('v1.1.8 synchronizes four approved English records and concordance',()=>{
 assert.equal(changes.length,4);
 const lines=read('0013.json').lines;
 const concordance=read('concordance.json').routes.flatMap(r=>r.scripts.flatMap(s=>s.lines));
 for(const c of changes){
  assert.equal(lines.find(r=>r.ref===c.ref).english,c.after);
  assert.equal(concordance.find(r=>r[0]===c.ref)[5],c.after);
 }
 assert.equal(read('index.json').version,'1.1.9');
});
