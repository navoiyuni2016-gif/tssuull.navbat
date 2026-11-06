// Optional developer check: Playwright + Chromium. Not needed on the terminal.
const {chromium}=require('playwright');const {spawn}=require('node:child_process');const path=require('node:path');const assert=require('node:assert/strict');
(async()=>{
  const server=spawn(process.env.NAVBAT_PYTHON||'python',[path.join(__dirname,'browser_server.py')]);let browser;
  try{
    const port=await new Promise((resolve,reject)=>{let output='';const timer=setTimeout(()=>reject(Error('Server startup timeout')),15000);server.stdout.on('data',data=>{output+=data;const match=output.match(/READY (\d+)/);if(match){clearTimeout(timer);resolve(match[1])}});server.on('exit',code=>{clearTimeout(timer);reject(Error('Server exit '+code))});server.stderr.on('data',data=>process.stderr.write(data));});
    browser=await chromium.launch({executablePath:process.env.NAVBAT_CHROME||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});
    const context=await browser.newContext();const errors=[];context.on('page',page=>page.on('pageerror',e=>errors.push(e.message)));
    const base='http://127.0.0.1:'+port;const page=await context.newPage();
    await page.goto(base+'/admin');await page.getByLabel('Login',{exact:true}).fill('admin');await page.getByLabel('Parol',{exact:true}).fill('browser-test-password-123');
    await page.getByRole('button',{name:'Saqlaş',exact:true}).click();await page.getByRole('heading',{name:'Administrator paneli'}).waitFor();
    await page.getByRole('button',{name:'Sozlamalar',exact:true}).click();await page.getByLabel('Universitet nomi',{exact:true}).waitFor();
    await page.getByRole('button',{name:'Xodimlar',exact:true}).click();await page.getByRole('heading',{name:'Xodimlar va ruxsatlar'}).waitFor();
    await page.getByRole('button',{name:'Hisobotlar',exact:true}).click();await page.getByText('Çiqarilgan çiptalar',{exact:true}).waitFor();
    await page.getByRole('button',{name:'Ovozlar',exact:true}).click();
    // Valid short PCM WAV fixture; never represented as a spoken production recording.
    const wav=Buffer.alloc(44+1600);wav.write('RIFF',0);wav.writeUInt32LE(wav.length-8,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(8000,24);wav.writeUInt32LE(16000,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(1600,40);
    await page.getByLabel('Ovoz vazifasi',{exact:true}).selectOption('digit_0');
    await page.locator('input[type=file]').setInputFiles({name:'zero.wav',mimeType:'audio/wav',buffer:wav});
    await page.locator('input[type=checkbox]').check();await page.getByRole('button',{name:'Ovozni yuklaş',exact:true}).click();await page.getByText('digit_0 — zero.wav',{exact:true}).waitFor();
    for(const slot of ['ticket','prefix_A','prefix_B','prefix_C','prefix_D','prefix_E','window',...Array.from({length:10},(_,i)=>'digit_'+i)]){
      const r=await context.request.post(base+'/api/audio/upload',{data:{slot,name:slot+'.wav',content:wav.toString('base64'),rights_confirmed:true}});assert.equal(r.ok(),true);
    }
    await context.request.post(base+'/api/settings',{data:{printer_mode:'windows',printer_name:'KPOS_80 Printer(1)',paper_width_mm:80}});
    // Printer completion is simulated here; real Windows paper output requires device testing.
    await context.route('**/api/print/status',route=>route.fulfill({json:{job:{status:'sent'}}}));
    await context.addInitScript(()=>{window.__printCalls=0;window.print=()=>window.__printCalls++;});
    const autoTV=await context.newPage();await autoTV.goto(base+'/tv?autostart=1');await autoTV.waitForFunction(()=>recorded.enabled);await autoTV.close();
    const english=await context.newPage();await english.goto(base+'/');
    await english.getByRole('button',{name:'English',exact:true}).click();
    await english.getByRole('button',{name:'Research and Innovation Services Sector',exact:true}).waitFor();await english.getByRole('heading',{name:'Choose a service',exact:true}).waitFor();assert(await english.getByText('Collect your ticket',{exact:false}).count()>0);
    assert.equal(await english.getByRole('button',{name:'Ўзбекча',exact:true}).count(),0);
    assert.equal(await english.locator('html').getAttribute('lang'),'en');
    const englishResponse=english.waitForResponse(r=>r.url().endsWith('/api/tickets')&&r.request().method()==='POST');
    await english.getByRole('button',{name:'Student Services Sector',exact:true}).click();
    const stored=await (await englishResponse).json();await english.waitForFunction(()=>!busy);
    assert.equal(await english.locator('.receipt-card,#terminal-printer-status').count(),0);assert.equal(await english.evaluate(()=>window.__printCalls),0);
    assert(await english.getByRole('heading',{name:'Choose a service',exact:true}).isVisible());
    const receipt=await context.request.get(base+'/receipt?request='+stored.request);assert((await receipt.text()).includes('People ahead'));
    await english.close();
    const terminal=await context.newPage();await terminal.goto(base+'/');
    await terminal.getByRole('button',{name:'Talabalarga xizmat körsatiş sektori',exact:true}).waitFor();
    assert.equal(await terminal.locator('nav').isHidden(),true);assert.equal(await terminal.locator('footer').isHidden(),true);assert.equal(await terminal.getByRole('heading',{name:'Xizmat turini tanlang',exact:true}).count(),1);assert.equal(await terminal.locator('.terminal-steps>div').count(),3);assert.equal(await terminal.locator('#terminal-printer-status').count(),0);
    await terminal.getByRole('button',{name:'Talabalarga xizmat körsatiş sektori',exact:true}).click();await terminal.waitForFunction(()=>!busy);assert.equal(await terminal.locator('.receipt-card').count(),0);assert.equal(await terminal.evaluate(()=>window.__printCalls),0);
    const tv=await context.newPage();await tv.addInitScript(()=>{window.__plays=[];const play=Audio.prototype.play;Audio.prototype.play=function(){window.__plays.push(this.src);return play.call(this)}});await tv.goto(base+'/tv-audio');await tv.locator('#tv-current-number').waitFor();
    await tv.getByRole('button',{name:'Ovozni yoqiş',exact:true}).click();
    await tv.waitForFunction(()=>recorded.enabled);await tv.locator('details').evaluate(e=>e.open=true);await tv.getByRole('button',{name:'Ovozni sinaş',exact:true}).click();
    try{await tv.waitForFunction(()=>window.__plays.length>=8&&!recorded.playing,{},{timeout:12000});}catch(e){console.error(await tv.evaluate(()=>({plays:window.__plays,status:document.querySelector('#sound-status')?.textContent,enabled:recorded.enabled,pending:recorded.pending,playing:recorded.playing,files:Object.keys(recorded.files)})));throw e;}
    await tv.getByRole('button',{name:'TV ekraniga ötiş',exact:true}).click();
    assert.equal(new URL(tv.url()).pathname,'/tv');assert.equal(await tv.locator('details').count(),0);assert.equal(await tv.getByRole('heading',{name:'Elektron navbat',exact:true}).count(),0);assert.equal(await tv.locator('footer').isVisible(),true);
    const staff=await context.newPage();await staff.goto(base+'/staff');assert.equal(await staff.locator('nav').isHidden(),true);assert.equal(await staff.getByRole('heading',{name:'Xodim paneli',exact:true}).count(),0);await staff.getByRole('button',{name:'Keyingisini çaqiriş',exact:true}).click();
    await tv.getByRole('cell',{name:'A001',exact:true}).waitFor();
    await tv.waitForFunction(()=>document.querySelector('#tv-current-number').getAnimations().some(a=>a.effect.getTiming().iterations===3));
    await tv.evaluate(()=>Promise.all(document.querySelector('#tv-current-number').getAnimations().map(a=>a.finished)));
    assert.equal(await tv.locator('#tv-current-number').evaluate(e=>getComputedStyle(e).opacity),'1');
    await staff.getByRole('button',{name:'Qayta çaqiriş',exact:true}).click();
    await tv.waitForFunction(()=>tvFlasher.current?.id===2&&document.querySelector('#tv-current-number').getAnimations().some(a=>a.effect.getTiming().iterations===3));
    await tv.evaluate(()=>Promise.all(document.querySelector('#tv-current-number').getAnimations().map(a=>a.finished)));
    assert.equal(await tv.locator('#tv-current-number').evaluate(e=>getComputedStyle(e).opacity),'1');
    await staff.getByRole('button',{name:/Xizmatni bo.*la.*$/}).click();
    await staff.getByRole('button',{name:'Yakunlaş',exact:true}).click();await staff.getByRole('button',{name:'Keyingisini çaqiriş',exact:true}).waitFor({state:'visible'});
    // Keep services visible, reject duplicate taps while printing, and retry the same ticket after an error.
    await context.unroute('**/api/print/status');let phase='pending',issued=0;
    await context.route('**/api/print/status',route=>route.fulfill({json:{job:{status:phase,error:phase==='failed'?'Printer offline':null}}}));
    terminal.on('request',r=>{if(r.url().endsWith('/api/tickets')&&r.method()==='POST')issued++;});
    await terminal.getByRole('button',{name:'Talabalarga xizmat körsatiş sektori',exact:true}).click();
    await terminal.waitForFunction(()=>busy&&ticket);await terminal.locator('.service-card').first().evaluate(e=>{e.click();e.click();});
    assert.equal(issued,1);assert.equal(await terminal.locator('.receipt-card,#receipt,#terminal-printer-status').count(),0);
    assert.equal(await terminal.locator('.service-card:disabled').count(),5);
    phase='failed';await terminal.locator('#kiosk-print-error').waitFor();await terminal.waitForFunction(()=>!busy);
    const sameRequest=await terminal.evaluate(()=>ticket.request);
    phase='sent';await terminal.locator('#kiosk-print-error button').click();await terminal.waitForFunction(()=>!busy&&ticket===null);
    assert.equal(issued,1);assert.equal(await terminal.evaluate(()=>sessionStorage.getItem('navbat-pending')),null);
    const jobs=await context.request.post(base+'/api/print/status',{data:{request:sameRequest}});assert(jobs.ok());
    assert.equal(await terminal.locator('#kiosk-print-error').count(),0);assert.equal(await terminal.evaluate(()=>window.__printCalls),0);
    assert.deepEqual(errors,[]);console.log('PASS browser: alphabet, admin pages, WAV upload, real WAV playback queue, terminal -> staff -> TV -> finish');
  }finally{if(browser)await browser.close();server.kill();}
})().catch(error=>{console.error(error);process.exitCode=1});
