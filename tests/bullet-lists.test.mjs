import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {scriptDataHref} from '../app/script/reader-data.mjs';
const read = file => JSON.parse(readFileSync(new URL('../public/script-data/'+file,import.meta.url)));
test('all eight source bullet lists retain separate English items',()=>{
 const index=read('index.json');
 const rows=index.routes.flatMap(route=>route.scripts.flatMap(script=>read(script.file).lines));
 const lists=rows.filter(row=>(row.english.match(/•/g)??[]).length>1);
 assert.equal(lists.length,8);
 for(const row of lists) {
  assert.equal(row.english.split('\n').filter(line=>/^•\s/.test(line)).length,(row.english.match(/•/g)??[]).length,row.ref);
  assert.equal(row.japanese.split('\n').filter(line=>/^\s*・/.test(line)).length,(row.english.match(/•/g)??[]).length,row.ref);
 }
});
test('hotfix JSON URLs bypass the earlier same-version browser cache',()=>{
 for(const file of ['index.json','0008.json','0092.json','concordance.json','hyperlink-entries.json']) {
  const url=new URL(scriptDataHref(file),'https://mao-tls.github.io/saihate-no-ima/script/');
  assert.equal(url.pathname,`/saihate-no-ima/script-data/${file}`);
  assert.equal(url.searchParams.get('rev'),'20261004-recurrence-carryovers');
 }
});
