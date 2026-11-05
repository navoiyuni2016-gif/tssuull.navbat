const test=require('node:test');const assert=require('node:assert/strict');
const Recorded=require('../web/recordings.js');const alphabet=require('../web/alphabet.js');
const flush=()=>new Promise(resolve=>setImmediate(resolve));
function fixture(){
  const played=[];class Audio{constructor(url){this.url=url}play(){played.push(this);return Promise.resolve()}pause(){this.paused=true}}
  const a=new Recorded(Audio,()=>{});a.configure(Object.fromEntries(['ticket','prefix_A','window',...Array.from({length:10},(_,n)=>'digit_'+n)].map(k=>[k,{url:k}])));return {a,played};
}

test('alphabet uses the requested Ş Ç Ğ Ö symbols',()=>{assert.equal(alphabet('Shahar, chipta, G‘oya, O‘zbekiston'),'Şahar, çipta, Ğoya, Özbekiston')});
test('missing files prevent enabling',async()=>{const a=new Recorded(class{},()=>{});await assert.rejects(a.enable(),/Yetishmayotgan/)});
test('recorded calls play clips and calls sequentially, recall is retained',async()=>{
  const {a,played}=fixture();await a.enable();played.length=0;
  a.enqueue([{id:2,number:2,window:3},{id:1,number:1,window:4}]);
  const expected=['ticket','prefix_A','digit_0','digit_0','digit_1','window','digit_4','ticket','prefix_A','digit_0','digit_0','digit_2','window','digit_3'];
  for(let i=0;i<expected.length;i++){assert.equal(played.length,i+1);assert.equal(played[i].url,expected[i]);played[i].onended();await flush()}
  assert.equal(a.playing,false);a.enqueue([{id:2,number:2,window:3}]);assert.equal(played.length,14);
  a.enqueue([{id:3,number:2,window:3}]);assert.equal(played.length,15);a.disable();await flush();
});
test('audio errors stop playback and retry the same call',async()=>{
  const {a,played}=fixture();await a.enable();played.length=0;a.enqueue([{id:1,number:1,window:1}]);played[0].onerror();await flush();assert.equal(a.enabled,false);assert.equal(a.pending.length,1);
  await a.enable();assert.equal(a.enabled,true);a.disable();await flush();assert.equal(a.playing,false);
});
