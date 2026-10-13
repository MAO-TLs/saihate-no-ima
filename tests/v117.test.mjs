import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
const read=file=>JSON.parse(readFileSync(new URL('../public/script-data/'+file,import.meta.url)));
const changes=JSON.parse(readFileSync(new URL('./fixtures/v117.json',import.meta.url)));
test('v1.1.7 projects exactly nine speaker labels and six structured lists',()=>{
  assert.equal(changes.filter(c=>c.field==='speakerEn').length,9);
  assert.equal(changes.filter(c=>c.field==='english').length,6);
  for(const c of changes){
    const file=c.ref.split(':')[2]+'.json';
    const row=read(file).lines.find(r=>r.ref===c.ref);
    assert.equal(row[c.field],c.after);
    if(c.field==='speakerEn'){assert.equal(c.before,'Jean');assert.equal(c.after,'Gene');}
    else {assert.equal(c.before.replace(/\s/g,''),c.after.replace(/\s/g,''));assert.equal(c.after.trim().split('\n').length,6);}
  }
});
test('v1.1.7 release metadata distinguishes repairs from unverified font appearance',()=>{
  const notes=readFileSync(new URL('../README.md',import.meta.url),'utf8');
  assert.match(notes,/Update-v1\.1\.6\.cmd/);
  assert.match(notes,/Undo-v1\.1\.7-update\.cmd/);
  assert.match(notes,/distorted-letter appearance has not been confirmed fixed/);
  assert.equal(read('index.json').version,'1.1.8');
  assert.equal(read('concordance.json').version,'1.1.8');
});
