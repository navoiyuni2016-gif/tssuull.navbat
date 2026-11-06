'use strict';
// Only OS-local voices are allowed. Remote speech services are never selected.
class QueueAnnouncer {
  constructor(synth, Utterance, status) {
    this.synth = synth;
    this.Utterance = Utterance;
    this.status = status;
    this.pending = [];
    this.enabled = false;
    this.speaking = false;
    this.voice = null;
    this.generation = 0;
    this.seen = new Set();
  }
  voices() {
    return this.synth ? this.synth.getVoices().filter(v => v.localService && /^(uz|ru)(-|_|$)/i.test(v.lang)) : [];
  }
  enable(voice) {
    if (!voice || !voice.localService) throw Error('Lokal ovoz topilmadi');
    this.voice = voice;
    this.enabled = true;
    this.status('Ovoz yoqilgan');
    this.pump();
  }
  disable() {
    this.generation++;
    this.enabled = false;
    this.pending = [];
    if (this.synth) this.synth.cancel();
    this.speaking = false;
    this.status('Ovoz o‘chirilgan');
  }
  text(call) {
    const digits = String(call.number).padStart(3, '0').split('').join(' ');
    const prefix=(call.label||'').match(/^[A-Z]+/)?.[0]||'A';
    const spokenPrefix=prefix==='A'&&!/^uz/i.test(this.voice.lang)?'А':prefix.split('').join(' ');
    return /^uz/i.test(this.voice.lang)
      ? `Diqqat! ${spokenPrefix} ${digits} raqamli chipta. ${call.window}-oynaga keling.`
      : `Внимание! Талон ${spokenPrefix} ${digits}. Подойдите к окну номер ${call.window}.`;
  }
  enqueue(calls) {
    for (const call of [...calls].sort((a,b) => a.id-b.id)) {
      if (this.seen.has(call.id)) continue;
      this.seen.add(call.id);
      // Calls received while muted are intentionally not announced later.
      if (this.enabled) this.pending.push(call);
    }
    this.pump();
  }
  test() {
    if (!this.enabled) throw Error('Avval ovozni yoqing');
    this.pending.push({number:1,window:1});
    this.pump();
  }
  pump() {
    if (!this.enabled || this.speaking || !this.pending.length) return;
    const call = this.pending.shift();
    const generation = this.generation;
    const utterance = new this.Utterance(this.text(call));
    utterance.voice = this.voice;
    utterance.lang = this.voice.lang;
    utterance.rate = 0.85;
    this.speaking = true;
    utterance.onend = () => { if (generation !== this.generation) return; this.speaking = false; this.pump(); };
    utterance.onerror = event => {
      if (generation !== this.generation) return;
      this.enabled = false;
      this.pending.unshift(call);
      this.speaking = false;
      this.status(`Ovoz xatosi: ${event.error || 'noma’lum'}. Ovoz yoqish tugmasini bosing.`);
    };
    try { this.synth.speak(utterance); }
    catch (error) { utterance.onerror({error:error.message}); }
  }
}
if (typeof module !== 'undefined') module.exports = QueueAnnouncer;
