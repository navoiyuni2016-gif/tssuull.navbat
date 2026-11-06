'use strict';
class RecordedAnnouncer {
  constructor(AudioClass, status) {
    this.AudioClass=AudioClass; this.status=status; this.files={}; this.prefix='A'; this.enabled=false;
    this.pending=[]; this.lastId=0; this.generation=0; this.playing=false; this.current=null;
  }
  configure(files,prefix='A',windows=[1,2,3,4,5]){this.files=files;this.prefixes=Array.isArray(prefix)?prefix:[prefix];this.prefix=this.prefixes[0]||'A';this.windows=windows;this.phraseMode=Object.keys(files).some(k=>/^window_[0-9]+$/.test(k)&&/^p[0-9]+\.(wav|mp3)$/i.test(files[k].name||''));}
  windowPhrase(n){const file=this.files['window_'+n];const m=file&&(file.name||'').match(/^p([0-9]+)\.(wav|mp3)$/i);return !!(m&&Number(m[1])===Number(n));}
  missing(){
    const prefixes=(this.prefixes||[this.prefix]).map(p=>'prefix_'+p);
    if(this.phraseMode)return [...prefixes.filter(k=>!this.files[k]),...this.windows.filter(n=>!this.windowPhrase(n)).map(n=>'window_'+n),...(Object.keys(this.files).some(k=>/^number_[1-9][0-9]*$/.test(k))?[]:['number_any'])];
    return ['ticket',...prefixes,'window',...Array.from({length:10},(_,n)=>'digit_'+n)].filter(k=>!this.files[k]);
  }
  async enable(){
    if(this.missing().length)throw Error('Yetishmayotgan ovozlar: '+this.missing().join(', '));
    // User gesture starts an actual clip, permitting subsequent chained playback.
    const first=this.phraseMode?this.files['prefix_'+this.prefix]:this.files.ticket;const audio=new this.AudioClass(first.url);audio.volume=0;
    await audio.play();audio.pause();audio.currentTime=0;
    this.enabled=true;this.status('Yuklangan ovozlar yoqildi');this.pump();
  }
  disable(){this.generation++;this.enabled=false;this.pending=[];if(this.current)this.current.pause();if(this.cancelClip)this.cancelClip();this.playing=false;this.status('Ovoz o‘chirilgan');}
  enqueue(calls){for(const c of [...calls].sort((a,b)=>a.id-b.id)){if(c.id<=this.lastId)continue;this.lastId=c.id;if(this.enabled)this.pending.push(c);}this.pump();}
  test(){if(!this.enabled)throw Error('Avval ovozni yoqing');const number=this.phraseMode?Math.min(...Object.keys(this.files).filter(k=>/^number_/.test(k)).map(k=>Number(k.slice(7)))):1;this.pending.push({label:this.prefix+String(number).padStart(3,'0'),number,window:this.phraseMode?this.windows[0]:1});this.pump();}
  clips(call){
    const digits=n=>String(n).split('').map(d=>'digit_'+d);
    const label=(call.label||'').match(/^([A-Z]+)([0-9]+)$/);
    const number=label?Number(label[2]):call.number;
    const prefix=label?label[1]:this.prefix;
    const numericKey='number_'+number;
    // s12.wav is the whole number 12; p5.wav is the whole window-5 phrase.
    // In phrase mode never fall back to the old, possibly misassigned pN digit slots.
    const numbers=this.phraseMode?[numericKey]:this.files[numericKey]?[numericKey]:digits(label?label[2]:String(number).padStart(3,'0'));
    if(this.phraseMode&&!this.windowPhrase(call.window))throw Error('Ovoz yo‘q: p'+call.window+'.wav');
    const tail=this.phraseMode?['window_'+call.window]:['window',...(this.files['window_'+call.window]?['window_'+call.window]:digits(call.window))];
    const keys=[...(this.files.attention?['attention']:[]),...(!this.phraseMode?['ticket']:[]),'prefix_'+prefix,...numbers,...tail];
    return keys.map(k=>{
      if(!this.files[k])throw Error('Ovoz yo‘q: '+k+(/^number_/.test(k)?' (s'+number+'.wav)':''));return this.files[k].url;
    });
  }
  clip(url,generation){return new Promise((resolve,reject)=>{
    const a=new this.AudioClass(url);this.current=a;
    const timer=setTimeout(()=>finish(Error('Ovoz juda uzun yoki yuklanmadi')),125000);
    const finish=error=>{clearTimeout(timer);a.onended=null;a.onerror=null;this.cancelClip=null;if(error){a.pause();reject(error)}else resolve();};
    this.cancelClip=()=>finish();a.onended=()=>finish();a.onerror=()=>finish(Error('Ovoz faylini ijro etib bo‘lmadi'));
    if(generation!==this.generation){finish();return;}
    Promise.resolve(a.play()).catch(finish);
  });}
  async pump(){
    if(!this.enabled||this.playing||!this.pending.length)return;
    this.playing=true;const generation=this.generation;
    try{
      while(this.enabled&&generation===this.generation&&this.pending.length){
        const call=this.pending[0];for(const url of this.clips(call)){
          if(!this.enabled||generation!==this.generation)return;
          await this.clip(url,generation);
        }
        if(generation===this.generation)this.pending.shift();
      }
    }catch(e){if(generation===this.generation){this.enabled=false;this.status(e.message+'. Ovozni qayta yoqing.');}}
    finally{if(generation===this.generation){this.playing=false;this.current=null;}}
  }
}
if(typeof module!=='undefined')module.exports=RecordedAnnouncer;
