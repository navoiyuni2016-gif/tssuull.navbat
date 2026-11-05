const test=require('node:test');const assert=require('node:assert/strict');const {TVCallFlasher,pulseTVNumbers}=require('../web/tv-flasher.js');
const tick=()=>new Promise(resolve=>setImmediate(resolve));
test('each new call and recall flashes serially, repeated polls do not flash again',async()=>{
 const seen=[],finish=[];const f=new TVCallFlasher(()=>{},call=>{seen.push(call.id);return new Promise(resolve=>finish.push(resolve));});
 f.enqueue([{id:2,number:1},{id:1,number:1}]);assert.deepEqual(seen,[1]);assert.equal(f.current.id,1);
 f.enqueue([{id:2,number:1},{id:3,number:1}]);finish[0]();await tick();assert.deepEqual(seen,[1,2]);finish[1]();await tick();assert.deepEqual(seen,[1,2,3]);finish[2]();await tick();assert.equal(f.current,null);assert.equal(f.running,false);
 f.enqueue([{id:3,number:1}]);await tick();assert.deepEqual(seen,[1,2,3]);
});
test('ticket and window use exactly three cycles and end visible',async()=>{
 const options=[];const frames=[];const el={animate:(keys,timing)=>{frames.push(keys);options.push(timing);return{finished:Promise.resolve()}}};
 await pulseTVNumbers([el,el]);assert.equal(options.length,2);for(const opt of options){assert.equal(opt.iterations,3);assert.equal(opt.duration,700)}for(const keyframes of frames){assert.equal(keyframes[0].opacity,1);assert.equal(keyframes.at(-1).opacity,1);}
});
