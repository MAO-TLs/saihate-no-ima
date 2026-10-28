import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=n=>JSON.parse(readFileSync(new URL('../public/script-data/'+n,import.meta.url)));
const changes=JSON.parse(readFileSync(new URL('./fixtures/v1110.json',import.meta.url)));
test('issue29 reviewed corrections match reader, search and copied previews',()=>{
 const search=new Map(read('concordance.json').routes.flatMap(r=>r.scripts.flatMap(s=>s.lines)).map(r=>[r[0],r]));
 const previews=Object.values(read('hyperlink-entries.json').entries).flatMap(e=>e.lines);
 assert.equal(changes.length,38);
 for(const c of changes){
  const row=read(c.ref.split(':')[2]+'.json').lines.find(r=>r.ref===c.ref);
  assert.deepEqual(row[c.field],c.after,c.ref);
  assert.deepEqual(search.get(c.ref)[{english:5,hyperlinks:10}[c.field]],c.after,c.ref);
  for(const preview of previews.filter(r=>r.ref===c.ref)) assert.deepEqual(preview[c.field],c.after,c.ref);
 }
});
