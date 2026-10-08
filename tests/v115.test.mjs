import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {test} from 'node:test';
import {scriptDataHref} from '../app/script/reader-data.mjs';

const read = name => JSON.parse(readFileSync(new URL('../public/script-data/' + name, import.meta.url)));
const hash = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
const changes = [
  {
    file: '0008.json',
    ref: 'saihate:story:0008:005406',
    before: '(I don’t know what to call it. But until just a moment ago, I know I was…)',
    after: '(I don’t know what to call it. But until just a moment ago, I definitely…)',
    baselineHash: '410b4c1084c67bdfcad8e7be0b5575ffe3f49e1614b8de443c3d744bedb8f44b',
  },
  {
    file: '0013.json',
    ref: 'saihate:story:0013:013418',
    before: 'He slipped his tongue inside and slowly explored every corner of her mouth.',
    after: 'She pushed her tongue inside and explored every corner of his mouth with painstaking care.',
    baselineHash: '8e3cf78932279bfe2458bb8f1c68a4a95cbb0a63c0c04373dbdd6d8ee5e00c4d',
  },
  {
    file: '0169.json',
    ref: 'saihate:hyperlinks:0169:000023',
    before: '“You too have wanted to understand those friends of yours, have you not?”',
    after: "“Surely you've wanted to understand that friend of yours completely too?”",
    baselineHash: '24ae447114e098227ffe6765a898b835f656dfd70974c5220b0624a9a664d3f6',
  },
  {
    file: '0170.json',
    ref: 'saihate:hyperlinks:0170:000022',
    before: 'Her own name, spoken without warning, sounded distant.',
    after: 'His own name, spoken without warning, sounded distant.',
    baselineHash: '0df1f0f13aef88ccae1bf596c61261ed9ea4480c7b5080f20baf4ad7e5a54632',
  },
];

test('v1.1.5 changes exactly four approved English fields', () => {
  for (const change of changes) {
    const current = read(change.file);
    const line = current.lines.find(row => row.ref === change.ref);
    assert.equal(line.english, change.after);
    line.english = change.before;
    assert.equal(hash(current), change.baselineHash, change.ref);
  }
});

test('v1.1.5 search corpus carries exactly the same four corrections', () => {
  const current = read('concordance.json');
  let count = 0;
  for (const route of current.routes) for (const script of route.scripts) for (const row of script.lines) {
    const change = changes.find(item => item.ref === row[0]);
    if (!change) continue;
    assert.equal(row[5], change.after);
    row[5] = change.before;
    count++;
  }
  assert.equal(count, 4);
  assert.equal(current.version, '1.1.6');
  current.version = '1.1.4';
  assert.equal(hash(current), 'a4f8cf63ca4668d3f5f70ebca48372734e2786fb1f4b4b9c46643e8c735ac177');
});

test('v1.1.5 exact recurrences remain exact', () => {
  const rows = new Map();
  for (const file of ['0007.json', '0013.json', '0169.json', '0170.json']) {
    for (const row of read(file).lines) rows.set(row.sourceId, row);
  }
  for (const [left, right] of [
    ['0013:013418', '0169:000111'],
    ['0169:000023', '0013:013807'],
    ['0170:000022', '0007:000036'],
  ]) {
    assert.equal(rows.get(left).japanese, rows.get(right).japanese);
    assert.equal(rows.get(left).english, rows.get(right).english);
  }
});

test('current reader metadata and cache revision match', () => {
  assert.equal(read('index.json').version, '1.1.6');
  assert.equal(
    new URL(scriptDataHref('0008.json'), 'https://example.com/script/').searchParams.get('rev'),
    'v1.1.6-20261009-c907173f2204',
  );
});
