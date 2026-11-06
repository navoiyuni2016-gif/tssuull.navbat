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
test('department letters require matching clips and use the actual printed label',async()=>{
  const {a}=fixture();a.configure(a.files,['A','B','C','D','E']);
  assert.deepEqual(a.missing(),['prefix_B','prefix_C','prefix_D','prefix_E']);
  for(const p of ['B','C','D','E'])a.files['prefix_'+p]={url:'prefix_'+p};
  assert.deepEqual(a.missing(),[]);assert.equal(a.clips({label:'B002',number:2,window:3})[1],'prefix_B');
});

test('legacy sN/pN pack speaks E012 and the actual calling window, ignoring misassigned digit files',async()=>{
  const {a,played}=fixture();
  const files={...a.files,prefix_E:{url:'sE.wav'},number_12:{url:'s12.wav'}};
  for(let n=1;n<=5;n++)files['window_'+n]={url:'p'+n+'.wav',name:'p'+n+'.wav'};
  a.configure(files,['A','E'],[1,2,3,4,5]);assert.deepEqual(a.missing(),[]);
  for(let n=1;n<=5;n++)assert.deepEqual(a.clips({label:'E012',number:999,window:n}),['sE.wav','s12.wav','p'+n+'.wav']);
  await a.enable();played.length=0;a.enqueue([{id:1,label:'E012',number:12,window:5}]);
  for(const url of ['sE.wav','s12.wav','p5.wav']){assert.equal(played.at(-1).url,url);played.at(-1).onended();await flush()}
  assert.equal(a.playing,false);
});
test('a missing whole number never leaves only the letter spoken',async()=>{
  const {a,played}=fixture();let status='';a.status=text=>status=text;
  const files={prefix_E:{url:'sE.wav'},number_1:{url:'s1.wav'},window_5:{url:'p5.wav',name:'p5.wav'}};
  a.configure(files,['E'],[5]);await a.enable();played.length=0;a.enqueue([{id:1,label:'E012',number:12,window:5}]);await flush();
  assert.equal(played.length,0);assert.match(status,/number_12.*s12.wav/);assert.equal(a.enabled,false);
});
test('legacy pack requires active windows and whole-number files, not fake zero or generic words',()=>{
 const {a}=fixture();a.configure({prefix_E:{url:'sE.wav'},window_1:{url:'p1.wav',name:'p1.wav'}},['E'],[1,5]);assert.deepEqual(a.missing(),['window_5','number_any']);
});
test('all A B S D E labels 001 through 500 select one shared whole number and the calling window',()=>{
 const {a}=fixture();const files={};for(const p of ['A','B','S','D','E'])files['prefix_'+p]={url:'letter-'+p};
 for(let n=1;n<=500;n++)files['number_'+n]={url:'S'+n+'.wav'};
 for(let n=1;n<=5;n++)files['window_'+n]={url:'P'+n+'.wav',name:'P'+n+'.wav'};
 a.configure(files,['A','B','S','D','E'],[1,2,3,4,5]);assert.deepEqual(a.missing(),[]);
 for(const p of ['A','B','S','D','E'])for(let n=1;n<=500;n++){const w=(n-1)%5+1;assert.deepEqual(a.clips({label:p+String(n).padStart(3,'0'),number:n,window:w}),['letter-'+p,'S'+n+'.wav','P'+w+'.wav']);}
});
