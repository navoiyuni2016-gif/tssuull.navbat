const test = require('node:test');
const assert = require('node:assert/strict');
const QueueAnnouncer = require('../web/announcer.js');
function fixture() {
  const local={name:'Local Russian',lang:'ru-RU',localService:true};
  const spoken=[];
  const synth={getVoices:()=>[local,{lang:'ru-RU',localService:false}],speak:u=>spoken.push(u),cancel:()=>{}};
  const announcer=new QueueAnnouncer(synth,class { constructor(text){this.text=text} },()=>{});
  return {announcer,local,spoken};
}
test('reject remote voices, select local speech only',()=>{
  const {announcer}=fixture();
  assert.equal(announcer.voices().length,1);
  assert.throws(()=>announcer.enable({localService:false}));
});
test('order, deduplication and recall without overlapping speech',()=>{
  const {announcer,local,spoken}=fixture();announcer.enable(local);
  announcer.enqueue([{id:2,number:2,window:3},{id:1,number:1,window:4}]);
  assert.equal(spoken.length,1);
  assert.match(spoken[0].text,/А 0 0 1.*4/);
  announcer.enqueue([{id:1,number:1,window:4},{id:3,number:2,window:3}]);
  spoken[0].onend();assert.equal(spoken.length,2);
  spoken[1].onend();assert.equal(spoken.length,3);
  spoken[2].onend();assert.equal(spoken.length,3);
});
test('muted history is not replayed, cancel callbacks cannot resume playback',()=>{
  const {announcer,local,spoken}=fixture();
  announcer.enqueue([{id:1,number:1,window:1}]);announcer.enable(local);
  assert.equal(spoken.length,0);
  announcer.test();announcer.disable();announcer.enable(local);announcer.test();
  spoken[0].onend();assert.equal(announcer.speaking,true);
  spoken[1].onend();assert.equal(announcer.speaking,false);
});
test('speech errors stop queue until explicitly enabled again',()=>{
  const {announcer,local,spoken}=fixture();announcer.enable(local);
  announcer.enqueue([{id:1,number:1,window:1},{id:2,number:2,window:2}]);
  spoken[0].onerror({error:'not-allowed'});
  assert.equal(announcer.enabled,false);assert.equal(spoken.length,1);
  announcer.enable(local);assert.equal(spoken.length,2);
  assert.match(spoken[1].text,/А 0 0 1/);
});
test('speech uses the actual department letter rather than a fixed A',()=>{
  const {announcer,local}=fixture();announcer.enable(local);
  assert.match(announcer.text({label:'B002',number:2,window:1}),/Талон B 0 0 2/);
});
