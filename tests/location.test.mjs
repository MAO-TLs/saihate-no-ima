import test from 'node:test';
import assert from 'node:assert/strict';
import { parseReaderLocation } from '../app/script/location.mjs';
const index = { routes: [{ id: 'story', scripts: [{id:'0004'}, {id:'0009'}] }, {id:'entries', scripts:[{id:'0004'}]}] };
test('Back restores corpus query/filter and Forward restores hyperlink target', () => {
  const source = 'http://localhost/script/?scope=all&q=At%20first&section=story';
  const destination = 'http://localhost/script/?scope=all&q=At%20first&section=story#saihate:story:0009:000011';
  assert.equal(parseReaderLocation(destination,index).pendingRef,'saihate:story:0009:000011');
  const back = parseReaderLocation(source,index);
  assert.equal(back.searchScope,'corpus'); assert.equal(back.corpusQuery,'At first'); assert.equal(back.corpusRouteId,'story'); assert.equal(back.pendingRef,'');
  const forward = parseReaderLocation(destination,index);
  assert.equal(forward.searchScope,'script'); assert.equal(forward.scriptId,'0009');
});
test('retired system links fall back to the story while image hyperlinks stay addressable',()=>{
 const withSystem={routes:[...index.routes,{id:'system',scripts:[{id:'0000'}]}]};
 const retired=parseReaderLocation('http://localhost/script/?route=system&script=0000#saihate:system:0000:000002',withSystem);
 assert.equal(retired.routeId,'story');
 assert.equal(retired.pendingRef,'');
 const image=parseReaderLocation('http://localhost/script/?route=entries&script=0004#saihate:entries:0004:entry-001230',withSystem);
 assert.equal(image.routeId,'entries');
 assert.equal(image.pendingRef,'saihate:entries:0004:entry-001230');
});
test('location validates route/script/filter and malformed encoded hashes are harmless', () => {
  const state = parseReaderLocation('http://localhost/script/?scope=all&q=x&section=missing#%E0%A4%A',index);
  assert.equal(state.searchScope,'corpus'); assert.equal(state.corpusRouteId,'all'); assert.equal(state.pendingRef,'');
  assert.equal(parseReaderLocation('http://localhost/script/?route=entries&script=0004',index).routeId,'entries');
});
