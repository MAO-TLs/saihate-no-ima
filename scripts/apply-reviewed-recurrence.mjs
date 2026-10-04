// Mechanical projection of a private source-reviewed ledger, never a prose sweep.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const review=JSON.parse(readFileSync(process.argv[2],'utf8'));
if(review.schema!=='saihate-source-bound-recurrence-hotfix-v1')throw Error('Wrong review ledger');
const dir='public/script-data/';
const read=name=>JSON.parse(readFileSync(dir+name,'utf8'));
const write=(name,data)=>writeFileSync(dir+name,JSON.stringify(data));
const index=read('index.json');
const files=[...new Set(index.routes.flatMap(r=>r.scripts.map(s=>s.file)))];
const payloads=new Map(files.map(file=>[file,read(file)]));
const rows=new Map([...payloads.values()].flatMap(p=>p.lines).map(row=>[row.sourceId,row]));
const hashes=[];
const hash=text=>createHash('sha256').update(text).digest('hex');
for(const [id,decision] of Object.entries(review.records)){
 const row=rows.get(id);if(!row)throw Error('Missing '+id);
 const original=row.english;
 const marked=decision.english_parts.slice(decision.metadata_count).join(' ').trim();
 const ranges=[];let english='',cursor=0;
 for(const match of marked.matchAll(/<h>(.*?)<\/h>/gs)){
  english+=marked.slice(cursor,match.index);const start=english.length;english+=match[1];
  ranges.push({start,end:english.length});cursor=match.index+match[0].length;
 }
 english+=marked.slice(cursor);
 if(english.includes('<h>')||english.includes('</h>'))throw Error('Bad marks '+id);
 if(ranges.length!==row.hyperlinks.length)throw Error('Link count changed '+id);
 row.english=english;
 row.hyperlinks=row.hyperlinks.map((link,i)=>({...link,...ranges[i]}));
 hashes.push({sourceId:id,englishHash:hash(english)});
}
const refs=new Map([...rows.values()].map(row=>[row.ref,row]));
for(const row of rows.values())for(const language of ['hyperlinks','japaneseHyperlinks']){
 for(const link of row[language]??[])for(const target of [link,...(link.alternatives??[])]){
  const destination=refs.get(target.targetRef);
  if(destination&&review.records[destination.sourceId]&&language==='hyperlinks')target.preview=destination.english;
 }
}
for(const [file,payload] of payloads){
 const rendered=JSON.stringify(payload);
 if(readFileSync(dir+file,'utf8')!==rendered)writeFileSync(dir+file,rendered);
}
const concordance=read('concordance.json');
for(const route of concordance.routes)for(const script of route.scripts)for(const compact of script.lines){
 const row=refs.get(compact[0]);if(!row)continue;
 compact[5]=row.english;compact[10]=row.hyperlinks;compact[11]=row.japaneseHyperlinks??[];
}
write('concordance.json',concordance);
const hover=read('hyperlink-entries.json');
for(const entry of Object.values(hover.entries))entry.lines=entry.lines.map(row=>refs.get(row.ref)??row);
write('hyperlink-entries.json',hover);
const groups=review.groups.map(group=>({members:group.members,type:group.type}));
const exceptions=['0009:008653','0009:008711','0007:000494','0007:000496'].map(sourceId=>({sourceId,englishHash:hash(rows.get(sourceId).english)}));
writeFileSync('tests/fixtures/recurrence.json',JSON.stringify({cases:hashes,groups,exceptions}));
console.log(JSON.stringify({editedRecords:hashes.length,groups:groups.length}));
