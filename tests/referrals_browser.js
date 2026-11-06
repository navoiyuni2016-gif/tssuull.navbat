// Real UI/API regression: private referrals never appear in the public kiosk/TV.
const {chromium}=require('playwright');const {spawn}=require('node:child_process');const assert=require('node:assert/strict');const path=require('node:path');const fs=require('node:fs');
(async()=>{let browser;const server=spawn(process.env.NAVBAT_PYTHON||'python',['tests/browser_server.py'],{cwd:path.resolve(__dirname,'..')});try{
 const port=await new Promise((resolve,reject)=>{let text='';server.stdout.on('data',x=>{text+=x;const m=text.match(/READY (\d+)/);if(m)resolve(m[1])});server.on('error',reject)});const base='http://127.0.0.1:'+port;
 browser=await chromium.launch({executablePath:process.env.NAVBAT_CHROME||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const admin=await browser.newContext({viewport:{width:1672,height:941}});const errors=[];browser.on('disconnected',()=>{});admin.on('page',p=>p.on('pageerror',e=>errors.push(e.message)));
 const login=await admin.request.post(base+'/api/login',{data:{name:'admin',password:'browser-test-password-123'}});assert(login.ok());
 for(let n=1;n<=5;n++)assert((await admin.request.post(base+'/api/users',{data:{name:'worker'+n,password:'referrals-browser-password',role:'staff',window:n}})).ok());
 const staff=await browser.newContext({viewport:{width:1672,height:941}});staff.on('page',p=>p.on('pageerror',e=>errors.push(e.message)));await staff.request.post(base+'/api/login',{data:{name:'worker5',password:'referrals-browser-password'}});
 const publicContext=await browser.newContext();const kiosk=await publicContext.newPage();await kiosk.goto(base+'/');await kiosk.locator('.service-card').first().waitFor();assert.equal(await kiosk.locator('.service-card').count(),5);assert.equal(await kiosk.locator('textarea').count(),0);assert.equal(await kiosk.getByRole('option',{name:/Administrator/}).count(),0);
 assert.equal((await publicContext.request.get(base+'/api/referrals')).status(),403);
 const issued=await (await publicContext.request.post(base+'/api/tickets',{data:{service:3,request:'private-referral-browser-request'}})).json();
 const page=await staff.newPage();await page.goto(base+'/staff');await page.getByRole('button',{name:'Keyingisini çaqiriş',exact:true}).click();
 await page.getByLabel('Boşqa xizmatga yönaltiriş',{exact:true}).selectOption('admin');const comment=page.getByLabel('Muammo izohi (majburiy)',{exact:true});await comment.fill('PRIVATE-CASE: hujjat <img src=x onerror=alert(1)> topilmadi');
 await page.waitForTimeout(2400);assert.equal(await comment.inputValue(),'PRIVATE-CASE: hujjat <img src=x onerror=alert(1)> topilmadi');
 const shots=process.env.NAVBAT_REFERRAL_SHOTS;if(shots){fs.mkdirSync(shots,{recursive:true});await page.screenshot({path:path.join(shots,'01-operator.png'),fullPage:true});}
 await page.getByRole('button',{name:'Yönaltiriş',exact:true}).click();await page.getByRole('heading',{name:'Administratorga yuborilgan murojaatlar',exact:true}).waitFor();assert(await page.getByRole('button',{name:'Keyingisini çaqiriş',exact:true}).isEnabled());
 assert.equal((await staff.request.get(base+'/api/referrals')).status(),403);assert.equal((await staff.request.post(base+'/api/referrals/resolve',{data:{id:1,status:'resolved',comment:'Forbidden'}})).status(),403);
 const stranger=await browser.newContext();await stranger.request.post(base+'/api/login',{data:{name:'worker1',password:'referrals-browser-password'}});const work=await (await stranger.request.get(base+'/api/work')).json();assert.deepEqual(work.referrals,[]);await stranger.close();
 const stateText=await (await publicContext.request.get(base+'/api/state')).text();assert(!stateText.includes('PRIVATE-CASE'));const calls=await (await publicContext.request.get(base+'/api/calls?after=0')).text();assert(!calls.includes('PRIVATE-CASE'));
 const ap=await admin.newPage();await ap.goto(base+'/admin');await ap.getByRole('button',{name:'Muammoli murojaatlar',exact:true}).click();await ap.getByRole('heading',{name:issued.label+' — Xalqaro aloqalar va akademik mobillik böyiça xizmat körsatiş sektori',exact:true}).waitFor();
 const form=ap.locator('.referral-form');await form.getByLabel('Natija izohi (majburiy)',{exact:true}).fill('Hujjat tekshirildi va tuzatildi');
 if(shots)await ap.screenshot({path:path.join(shots,'02-administrator.png'),fullPage:true});
 await form.getByRole('button',{name:'Saqlaş',exact:true}).click();await ap.getByText('Muammoli murojaatlar yöq',{exact:true}).waitFor();await ap.getByLabel('Murojaat holati',{exact:true}).selectOption('resolved');await ap.getByText('Hujjat tekshirildi va tuzatildi',{exact:true}).waitFor();
 const cases=await (await admin.request.get(base+'/api/referrals')).json();assert.equal(cases.referrals[0].status,'resolved');assert.equal(cases.referrals[0].operator,'worker5');assert.equal(cases.referrals[0].resolved_by,'admin');
 await page.getByText('Hal qilindi',{exact:true}).waitFor();
 await ap.getByRole('button',{name:'Hisobotlar',exact:true}).click();await ap.getByText('Hujjat tekshirildi va tuzatildi',{exact:true}).waitFor();const report=await (await admin.request.get(base+'/api/reports')).json();assert.equal(report.referrals.resolved,1);assert.equal(report.served,1);assert.equal(report.employees.admin.served,1);
 for(const format of ['xlsx','docx','pdf'])assert((await admin.request.get(base+'/api/reports/export?format='+format)).ok());
 if(shots)await ap.screenshot({path:path.join(shots,'03-hisobot.png'),fullPage:true});
 assert.equal(await kiosk.locator('textarea').count(),0);assert.deepEqual(errors,[]);console.log('PASS referrals UI: five operators supported, comment persists, admin resolves, staff sees outcome, private data excluded from kiosk/TV, exports succeed');
}finally{if(browser)await browser.close();server.kill()}})().catch(e=>{console.error(e);process.exitCode=1});
