import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=file=>JSON.parse(readFileSync(new URL('../public/script-data/'+file,import.meta.url)));
const rows=read('index.json').routes.flatMap(route=>route.scripts.flatMap(script=>read(script.file).lines));
const deferred=new Set(['0157:000196','0157:000238','0158:000077','0158:000096']);

test('source-reviewed non-explicit English has no flagged Japanese carryovers',()=>{
 const unwanted=/\b(?:moe|senpai|sempai|kouhai|kohai|sensei|kunoichi|nyoiju|eroge|nyahaha|nyaunu|nyaaah|nyoo|nya|kawaii|baka|sugoi|nakama|tsundere|yandere|waifu|husbando|desu|[A-Za-z]+-(?:chan|kun|san|sama|tan|chin|chi|dono))\b/i;
 for(const row of rows) {
  if(deferred.has(row.sourceId))continue;
  const text=(row.speakerEn+' '+row.english).replaceAll('5-Moe-DIPT','').replaceAll('Ume-chan Candies','').replaceAll('Super Kunoichi','');
  assert.equal(unwanted.test(text),false,row.ref);
 }
});

test('proper source names and established layout are retained',()=>{
 assert.ok(rows.find(row=>row.sourceId==='0006:001593').english.includes('5-Moe-DIPT'));
 assert.ok(rows.find(row=>row.sourceId==='0010:003091').english.includes('Ume-chan Candies'));
 assert.ok(rows.find(row=>row.sourceId==='0007:000790').english.includes('Super Kunoichi'));
 const row=rows.find(row=>row.sourceId==='0166:000027');
 assert.ok(row.english.startsWith('—older sisters ftw.\n'));
 assert.equal(row.english.split('\n').length,3);
});
