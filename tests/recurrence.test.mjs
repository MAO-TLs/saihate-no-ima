import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const read=file=>JSON.parse(readFileSync(new URL('../public/script-data/'+file,import.meta.url)));
const rows=new Map(read('index.json').routes.flatMap(route=>route.scripts.flatMap(script=>read(script.file).lines)).map(row=>[row.sourceId,row]));
const fixture=JSON.parse(readFileSync(new URL('fixtures/recurrence.json',import.meta.url)));
const hash=text=>createHash('sha256').update(text).digest('hex');
const normalized=text=>text.replace(/[\s\u2060]+/g,' ').trim();
test('all 39 source-reviewed recurrence corrections retain their approved text',()=>{
 assert.equal(fixture.cases.length,39);
 for(const row of fixture.cases)assert.equal(hash(rows.get(row.sourceId).english),row.englishHash,row.sourceId);
});
test('fixed repeated passages match without flattening contextual exceptions',()=>{
 for(const group of fixture.groups){
  if(group.type==='contextual_tense')continue;
  const members=group.members.map(id=>rows.get(id));
  if(group.type==='shared_subpassage'){
   assert.ok(normalized(members[1].japanese).includes(normalized(members[0].japanese)),group.members.join(','));
   assert.ok(normalized(members[1].english).includes(normalized(members[0].english)),group.members.join(','));
  }else{
   for(const member of members.slice(1)){
    assert.equal(member.japanese.replace(/\s/g,''),members[0].japanese.replace(/\s/g,''),member.ref);
    assert.equal(normalized(member.english),normalized(members[0].english),member.ref);
   }
  }
 }
 for(const exception of fixture.exceptions)assert.equal(hash(rows.get(exception.sourceId).english),exception.englishHash,exception.sourceId);
 assert.ok(rows.get('0011:000734').english.includes('Nothing will change.'));
});
