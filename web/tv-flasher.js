'use strict';
class TVCallFlasher {
  constructor(show,pulse){this.show=show;this.pulse=pulse;this.lastId=0;this.pending=[];this.current=null;this.running=false;}
  enqueue(calls){for(const call of [...calls].sort((a,b)=>a.id-b.id)){if(call.id<=this.lastId)continue;this.lastId=call.id;this.pending.push(call);}this.pump();}
  async pump(){
    if(this.running)return;this.running=true;
    try{while(this.pending.length){this.current=this.pending.shift();this.show();try{await this.pulse(this.current)}catch{} }}
    finally{this.current=null;this.running=false;this.show();}
  }
}
function pulseTVNumbers(elements){
  const reduced=typeof matchMedia==='function'&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  const frames=reduced?[{filter:'brightness(1)'},{filter:'brightness(.8)',offset:.5},{filter:'brightness(1)'}]:[{opacity:1},{opacity:.12,offset:.5},{opacity:1}];
  return Promise.all(elements.filter(Boolean).map(el=>{
    if(typeof el.animate==='function')return el.animate(frames,{duration:700,iterations:3,easing:'ease-in-out'}).finished.catch(()=>{});
    el.classList.add('call-flash');return new Promise(resolve=>setTimeout(()=>{el.classList.remove('call-flash');resolve()},2100));
  }));
}
if(typeof module!=='undefined')module.exports={TVCallFlasher,pulseTVNumbers};
