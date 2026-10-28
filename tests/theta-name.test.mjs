import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = file => JSON.parse(readFileSync(new URL('../public/script-data/'+file,import.meta.url)));
test('theta handle stays θ; three reviewed full names incorporate the removed reading',()=>{
 const fullNames=new Set(['0008:000997','0008:001202','0008:002820']);
 const check=(id,speaker,text)=>{assert.doesNotMatch(speaker??'',/\bTheta\b/);if(fullNames.has(id)) assert.match(text,/Francis Theta/);else assert.doesNotMatch(text,/\bTheta\b/);};
 const index=read('index.json');
 const rows=index.routes.flatMap(route=>route.scripts.flatMap(script=>read(script.file).lines));
 for(const row of rows) check(row.sourceId,row.speakerEn,row.english);
 const byId=new Map(rows.map(row=>[row.sourceId,row]));
 for(const id of ['0008:000996','0008:001200']) assert.equal(byId.get(id).english,'');
 const concordance=read('concordance.json');
 for(const route of concordance.routes) for(const script of route.scripts) for(const row of script.lines) check(row[0].split(':').slice(-2).join(':'),row[3],row[5]);
 const previews=read('hyperlink-entries.json');
 for(const entry of Object.values(previews.entries)) for(const row of entry.lines) check(row.sourceId,row.speakerEn,row.english);
});
