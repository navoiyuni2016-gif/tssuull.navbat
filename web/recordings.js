'use strict';
class RecordedAnnouncer {
  constructor(AudioClass, status) {
    this.AudioClass=AudioClass; this.status=status; this.files={}; this.prefix='A'; this.enabled=false;
    this.pending=[]; this.lastId=0; this.generation=0; this.playing=false; this.current=null;
  }
  configure(files,prefix='A'){this.files=files;this.prefixes=Array.isArray(prefix)?prefix:[prefix];this.prefix=this.prefixes[0]||'A';}
  missing(){return ['ticket',...(this.prefixes||[this.prefix]).map(p=>'prefix_'+p),'window',...Array.from({length:10},(_,n)=>'digit_'+n)].filter(k=>!this.files[k]);}
  async enable(){
    if(this.missing().length)throw Error('Yetishmayotgan ovozlar: '+this.missing().join(', '));
    // User gesture starts an actual clip, permitting subsequent chained playback.
    const audio=new this.AudioClass(this.files.ticket.url);audio.volume=0;
    await audio.play();audio.pause();audio.currentTime=0;
    this.enabled=true;this.status('Yuklangan ovozlar yoqildi');this.pump();
  }
  disable(){this.generation++;this.enabled=false;this.pending=[];if(this.current)this.current.pause();if(this.cancelClip)this.cancelClip();this.playing=false;this.status('Ovoz o‘chirilgan');}
  enqueue(calls){for(const c of [...calls].sort((a,b)=>a.id-b.id)){if(c.id<=this.lastId)continue;this.lastId=c.id;if(this.enabled)this.pending.push(c);}this.pump();}
  test(){if(!this.enabled)throw Error('Avval ovozni yoqing');this.pending.push({number:1,window:1});this.pump();}
  clips(call){
    const digits=n=>String(n).split('').map(d=>'digit_'+d);
    const number=this.files['number_'+call.number]?['number_'+call.number]:digits(String(call.number).padStart(3,'0'));
    const window=this.files['window_'+call.window]?['window_'+call.window]:digits(call.window);
    return [...(this.files.attention?['attention']:[]),'ticket','prefix_'+((call.label||this.prefix).match(/^[A-Z]+/)||[this.prefix])[0],...number,'window',...window].map(k=>{
      if(!this.files[k])throw Error('Ovoz yo‘q: '+k);return this.files[k].url;
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
