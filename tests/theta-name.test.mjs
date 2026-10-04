import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = file => JSON.parse(readFileSync(new URL('../public/script-data/'+file,import.meta.url)));
test('the user-selected theta name is always θ in English reader data',()=>{
 const index=read('index.json');
 const rows=index.routes.flatMap(route=>route.scripts.flatMap(script=>read(script.file).lines));
 for(const row of rows) assert.doesNotMatch([row.speakerEn,row.english].join('\n'),/\bTheta\b/);
 const byId=new Map(rows.map(row=>[row.sourceId,row]));
 for(const id of ['0008:000996','0008:000997','0008:001200','0008:001202']) assert.match(byId.get(id).english,/θ/);
 const concordance=read('concordance.json');
 for(const route of concordance.routes) for(const script of route.scripts) for(const row of script.lines) assert.doesNotMatch([row[3],row[5]].join('\n'),/\bTheta\b/);
 const previews=read('hyperlink-entries.json');
 for(const entry of Object.values(previews.entries)) for(const row of entry.lines) assert.doesNotMatch([row.speakerEn,row.english].join('\n'),/\bTheta\b/);
});
