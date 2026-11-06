'use strict';
document.body.classList.toggle('terminal',location.pathname==='/');
document.body.classList.toggle('staff',location.pathname==='/staff');
document.body.classList.toggle('admin',location.pathname==='/admin');
const main=document.querySelector('#main');
const APP_TITLE='TOŞDÖTAU — elektron navbat tizimi';
document.title=APP_TITLE;
const isTV=()=>location.pathname==='/tv'||location.pathname==='/tv-audio';
let state,lang='uz',ticket,requestId,busy=false,started=false,lastService;
let operatorDepartment='';
const labels={uz:['Xizmat turini tanlang','CHIPTA','OYNA','Chiptani chop etish','Bosh sahifa'],ru:['Выберите услугу','БИЛЕТ','ОКНО','Печать билета','Главная'],en:['Choose a service','TICKET','WINDOW','Print ticket','Home']};
const terminalCopy={
 uz:{brand:'TOŞDÖTAU — elektron navbat tizimi',recover:'Oxirgi so‘rovni tiklash',recoverFirst:'Avval oxirgi so‘rovni tiklang',ahead:'Oldinda kutayotganlar',checking:'Bosma holati tekshirilmoqda…',preview:'Sinov rejimi: brauzer orqali chop etish yoki PDF sifatida saqlash',pending:'Printer navbatida',dispatching:'Printerga yuborilmoqda',sent:'Windows bosma navbatiga yuborildi. Qog‘oz chiqqanini tekshiring.',failed:'Bosma xatosi. Printer sozlamalarini tekshiring.',uncertain:'Bosma natijasi noma’lum. Qog‘ozni tekshiring.',missing:'Bosma holati yo‘q',offline:'Bosma holatini olib bo‘lmadi. Mavjud chiptani qayta chop etishingiz mumkin.',service:'Xizmat',pdf:'HTML / PDF ko‘rinishi'},
 ru:{brand:'TOŞDÖTAU — электронная очередь',recover:'Восстановить последний запрос',recoverFirst:'Сначала восстановите предыдущий запрос',ahead:'Перед вами в очереди',checking:'Проверяем печать…',preview:'Тестовый режим: печать в браузере или сохранение PDF',pending:'В очереди печати',dispatching:'Отправляем на принтер',sent:'Отправлено в очередь печати Windows. Проверьте бумагу.',failed:'Ошибка печати. Проверьте настройки принтера.',uncertain:'Результат печати неизвестен. Проверьте бумагу.',missing:'Нет данных о печати',offline:'Статус печати недоступен. Можно повторно распечатать тот же билет.',service:'Услуга',pdf:'Просмотр HTML / PDF'},
 en:{brand:'TOŞDÖTAU — electronic queue',recover:'Recover last request',recoverFirst:'Recover the previous request first',ahead:'People ahead',checking:'Checking print status…',preview:'Preview mode: print in your browser or save as PDF',pending:'Queued for printing',dispatching:'Sending to printer',sent:'Sent to the Windows print queue. Check the paper output.',failed:'Printing failed. Check the printer settings.',uncertain:'Print result is unknown. Check the paper output.',missing:'No print status available',offline:'Print status is unavailable. You can reprint the same ticket.',service:'Service',pdf:'HTML / PDF preview'}
};
const terminalGuide={
 uz:{title:'Xizmat turini tanlang',hint:'Kerakli bo‘limni bosing va navbat chiptasini oling',steps:['Xizmatni tanlang','Chiptani oling','Navbatingizni kuting'],note:'Chiptani olgach, navbatingizni katta ekranda kuzating',preview:'PDF / sinov rejimi',configured:'Printer sozlangan'},
 ru:{title:'Выберите услугу',hint:'Нажмите на нужный отдел и получите билет',steps:['Выберите услугу','Получите билет','Ожидайте вызова'],note:'Получив билет, следите за своим номером на экране',preview:'Режим PDF / предпросмотра',configured:'Принтер настроен'},
 en:{title:'Choose a service',hint:'Tap the department you need and collect your ticket',steps:['Choose a service','Collect your ticket','Wait for your turn'],note:'After collecting your ticket, watch the display for your number',preview:'PDF / preview mode',configured:'Printer configured'}
};


function audioPrefixes(){const list=[...(state?.services||[]).map(s=>s.prefix),...[...(state?.calls||[]),...(state?.window_calls||[]),...(state?.queue||[])].map(c=>(c.label||'').match(/^[A-Z]+/)?.[0])].filter(Boolean);return [...new Set(list.length?list:[state?.settings.prefix||'A'])];}
const copy=key=>terminalCopy[lang][key];
function updateBrand(){
 if(!state)return;
 document.body.dataset.customBackground=String(!!state.custom_background);
 document.querySelector('.seal').classList.toggle('has-logo',!!state.custom_logo);
 document.querySelector('#university').textContent=APP_TITLE;
 document.querySelector('.seal').title=state.university;
 document.querySelector('footer span:not(#connection)').textContent=isTV()?'Navbatingizni ekranda kuzatib boring':'Universitet elektron navbat tizimi';
 document.querySelector('#brand-subtitle').textContent=state.university;
}

const statusNames={waiting:'Kutilmoqda',called:'Chaqirildi',serving:'Xizmat ko‘rsatilmoqda',done:'Yakunlandi',absent:'Kelmadi'};
function el(tag,text,parent=main){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;parent.append(e);return e}
function button(text,fn,parent=main){const b=el('button',text,parent);b.type='button';b.onclick=async()=>{b.disabled=true;try{await fn()}catch(e){alert(e.message)}finally{b.disabled=false}};return b}
function icon(name){
  const paths={
    touch:['M9 11V6a2 2 0 0 1 4 0v7','M13 11a2 2 0 0 1 3 1 2 2 0 0 1 3 1 2 2 0 0 1 3 2l-2 7H9l-6-8a2 2 0 0 1 3-2l3 3','M5 8a6 6 0 0 1 12-3'],
    printer:['M6 9V3h12v6','M6 18H3V9h18v9h-3','M6 14h12v8H6z','M17 11h.01'],
    clock:['M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z','M12 6v6l4 2'],
    student:['M3 9 12 4l9 5-9 5-9-5Z','M6 11v6c4 3 8 3 12 0v-6','M21 9v7'],
    research:['M9 3h6','M10 3v7L4 20h16l-6-10V3','M8 14h8','M10 17h.01M14 18h.01'],
    globe:['M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z','M3 12h18','M12 3c5 5 5 13 0 18-5-5-5-13 0-18Z'],
    work:['M4 7h16a1 1 0 0 1 1 1v11H3V8a1 1 0 0 1 1-1Z','M8 7V4h8v3','M3 12c5 3 13 3 18 0','M10 12v3h4v-3'],
    finance:['M5 3h14v18H5z','M8 6h8v4H8z','M8 14h1m3 0h1m3 0h.01M8 17h1m3 0h1m3 0h.01'],
    arrow:['M5 12h14','m14 7 5 5-5 5'],
    next:['M4 12h15','m13 6 6 6-6 6'],
    recall:['M4 10a8 8 0 1 1 0 6','M4 4v6h6'],
    start:['m9 5 11 7-11 7V5Z'],
    finish:['m5 12 5 5L20 7'],
    absent:['m6 6 12 12','M18 6 6 18'],
    audio:['M4 10h4l5-5v14l-5-5H4z','M16 8c3 2 3 6 0 8','M19 5c5 4 5 10 0 14'],
    settings:['M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8Z','M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10 10 2 2M19 5l-2 2M7 17l-2 2'],
    services:['M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z'],
    windows:['M3 4h18v14H3z','M8 22h8M12 18v4M3 8h18'],
    users:['M8 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z','M2 21v-2a6 6 0 0 1 12 0v2','M16 5a4 4 0 0 1 0 8M18 16a5 5 0 0 1 4 5'],
    reports:['M4 3v18h17','M9 16v-4m5 4V7m5 9v-6'],
    logout:['M10 4H4v16h6','M10 12h11m-4-4 4 4-4 4'],
  };
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');svg.classList.add('icon');
  for(const d of paths[name]||paths.services){const p=document.createElementNS(svg.namespaceURI,'path');p.setAttribute('d',d);svg.append(p);}
  return svg;
}
async function api(path,body){const r=await fetch('/api/'+path,body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{});const result=await r.json();if(!r.ok){const error=Error(result.error);error.status=r.status;throw error}return result}
function number(n){return (state?.settings.prefix||'A')+String(n).padStart(3,'0')}
function clear(){main.replaceChildren();}
function heading(text){clear();el('h2',text)}
function field(form,text,type='text',value=''){const label=el('label',text,form);const input=el('input',undefined,label);input.type=type;input.value=value;if(type==='file')decorateFile(input);return input}
function decorateFile(input){
  const wrap=document.createElement('span');wrap.className='file-picker';input.parentNode.insertBefore(wrap,input);wrap.append(input);
  const choose=el('span','Faylni tanlash',wrap);choose.className='file-choose';choose.prepend(icon('arrow'));
  const name=el('span','Fayl tanlanmagan',wrap);name.className='file-name';
  input.addEventListener('change',()=>{name.textContent=input.files[0]?.name||'Fayl tanlanmagan';name.classList.toggle('technical',!!input.files[0]);});
  input.resetLabel=()=>{name.classList.remove('technical');name.textContent='Fayl tanlanmagan';};
}

function choice(form,text,items,value){const label=el('label',text,form);const s=el('select',undefined,label);for(const [key,name] of items){const option=el('option',name,s);option.value=key;option.selected=String(key)===String(value)}return s}
function submitForm(form,handler){const out=el('p','',form);out.setAttribute('role','status');const b=el('button','Saqlash',form);b.type='submit';form.onsubmit=async e=>{e.preventDefault();b.disabled=true;try{out.textContent='Saqlanmoqda…';await handler();out.textContent='Saqlandi'}catch(e){out.textContent=e.message}finally{b.disabled=false}}}
function newRequest(){return Array.from(crypto.getRandomValues(new Uint8Array(24)),x=>x.toString(16).padStart(2,'0')).join('')}
function remember(value){try{if(value)sessionStorage.setItem('navbat-pending',JSON.stringify(value));else sessionStorage.removeItem('navbat-pending')}catch{}}
function recovered(){try{return JSON.parse(sessionStorage.getItem('navbat-pending'))}catch{return null}}
function serviceName(s){return (lang==='en'?s.name_en:lang==='ru'?s.name_ru:s.name)||s.name}
function terminal(){
  document.documentElement.lang=lang;clear();document.querySelector('.languages')?.remove();updateBrand();
  const languages=el('div',undefined,document.querySelector('header'));languages.className='languages technical';
  for(const [k,n,name] of [['uz','UZ','Özbekça'],['ru','RU','Русский'],['en','EN','English']]){const b=button(n,()=>{lang=k;terminal()},languages);b.className=k===lang?'language active':'language';b.setAttribute('aria-pressed',String(k===lang));b.setAttribute('aria-label',name);}
  const intro=el('section');intro.className='terminal-intro';el('h2',terminalGuide[lang].title,intro);el('p',terminalGuide[lang].hint,intro);
  const pending=recovered();
  if(pending)button(copy('recover'),()=>obtain(pending.service,pending.request));
  const services=el('div');services.id='services';
  state.services.forEach((s,i)=>{
    const b=button('',()=>obtain(s.id),services);b.className='service-card service-'+(i%5+1);
    const badge=el('span',undefined,b);badge.className='service-icon';badge.append(icon(['student','research','globe','work','finance'][i%5]));
    b.setAttribute('aria-label',serviceName(s));
    const titles={uz:['Talabalar xizmatlari','Ilm-fan va innovatsiya','Xalqaro aloqalar','Marketing va amaliyot','Buxgalteriya'],ru:['Услуги студентам','Наука и инновации','Международные связи','Маркетинг и практика','Бухгалтерия'],en:['Student services','Research and innovation','International relations','Marketing and internships','Accounting']};
    const original=['Talabalarga xizmat ko‘rsatish sektori','Ilmiy va innovatsion faoliyat bo‘yicha xizmat ko‘rsatish sektori','Xalqaro aloqalar va akademik mobillik bo‘yicha xizmat ko‘rsatish sektori','Marketing va amaliyotlarni tashkil etish','Buxgalteriya bo‘yicha xizmat ko‘rsatish sektori'];
    const known=s.id>=1&&s.id<=5&&uzbekAlphabet(s.name)===uzbekAlphabet(original[s.id-1]);
    const words=el('span',undefined,b);words.className='service-copy';el('span',known?titles[lang][s.id-1]:serviceName(s),words).className='service-name';if(known)el('span',serviceName(s),words).className='service-description';
    const arrow=el('span',undefined,b);arrow.className='service-arrow';arrow.append(icon('arrow'));
    const ordinal=el('span',String(i+1).padStart(2,'0'),b);ordinal.className='service-ordinal';ordinal.setAttribute('aria-hidden','true');
  });
  const guide=el('div');guide.className='terminal-steps';
  terminalGuide[lang].steps.forEach((text,i)=>{const step=el('div',undefined,guide);step.append(icon(['touch','printer','clock'][i]));el('span',(i+1)+'. '+text,step);});
  const bottom=el('div');bottom.className='terminal-bottom';el('p',terminalGuide[lang].note,bottom);
}
async function obtain(service,retry){
  if(busy)return;busy=true;setKioskBusy(true);
  try{
    if(state.settings.printer_mode!=='windows')throw Error({uz:'Printer sozlanmagan. Xodimga murojaat qiling.',ru:'Принтер не настроен. Обратитесь к сотруднику.',en:'Printer is not configured. Please contact a staff member.'}[lang]);
    const pending=recovered();
    if(pending&&!retry){if(pending.service!==service)throw Error(copy('recoverFirst'));retry=pending.request;}
    if(retry&&pending?.lang){lang=pending.lang;document.documentElement.lang=lang;}
    requestId=retry||newRequest();lastService=service;remember({service,request:requestId,lang});
    document.querySelector('#kiosk-print-error')?.remove();
    ticket=await api('tickets',{service,request:requestId,lang});
    await completeKioskPrint();
  }catch(error){if(!ticket&&error.status===400){remember(null);requestId=null;}kioskPrintError(error);}finally{busy=false;setKioskBusy(false)}
}
function setKioskBusy(value){document.querySelectorAll('.service-card,.language').forEach(b=>b.disabled=value);main.setAttribute('aria-busy',String(value));}
async function completeKioskPrint(){
  setKioskBusy(true);
  for(let attempt=0;attempt<90;attempt++){
    const job=(await api('print/status',{request:ticket.request})).job;
    if(job)ticket.last_print_job=job.id;
    if(job?.status==='printed'||job?.status==='sent'){remember(null);ticket=null;requestId=null;document.querySelector('#kiosk-print-error')?.remove();return;}
    if(!job||!['pending','printing','dispatching'].includes(job.status))throw Error(job?.error||copy(job?.status||'missing'));
    await new Promise(resolve=>setTimeout(resolve,500));
  }
  throw Error(copy('uncertain'));
}
function kioskPrintError(error){
  document.querySelector('#kiosk-print-error')?.remove();
  const box=el('div');box.id='kiosk-print-error';box.className='kiosk-print-error';box.setAttribute('role','alert');el('p',error.message,box);
  if(ticket)button({uz:'Qog‘ozni tekshirib, shu chiptani qayta chop etish',ru:'Проверить бумагу и повторить печать билета',en:'Check paper and reprint the same ticket'}[lang],async()=>{
    if(busy)return;busy=true;setKioskBusy(true);
    try{ticket.reprintAttempt=ticket.reprintAttempt||newRequest();await api('print',{request:ticket.request,previous_job:ticket.last_print_job,attempt:ticket.reprintAttempt});ticket.reprintAttempt=null;await completeKioskPrint();}catch(e){kioskPrintError(e)}finally{busy=false;setKioskBusy(false)}
  },box);
}

function login(){
  heading('Tizimga kirish');const form=el('form');form.className='card login-form';
  const name=field(form,'Login');name.autocomplete='username';name.required=true;
  const pass=field(form,'Parol','password');pass.autocomplete='current-password';pass.required=true;
  submitForm(form,async()=>{await api('login',{name:name.value,password:pass.value});await route()});
}
async function staff(){
  let data;try{data=await api('work')}catch{login();return}
  clear();const top=el('div');top.className='staff-topbar';
  const windowTag=el('span',data.window+'-oyna',top);windowTag.className='window-tag';windowTag.prepend(icon('windows'));
  const exit=button('Chiqish',async()=>{await api('logout',{});login()},top);exit.className='ghost';exit.prepend(icon('logout'));
  const holder=el('section');holder.id='staff-data';await staffData(data);
}
async function staffData(data){
  const holder=document.querySelector('#staff-data');if(!holder)return;
  holder.replaceChildren();holder.className='staff-layout';
  const waiting=data.tickets.filter(t=>t.status==='waiting');const active=data.tickets.find(t=>t.status!=='waiting');
  const current=el('section',undefined,holder);current.className='card current-ticket';
  const cap=el('div',undefined,current);cap.className='card-caption';el('span','Joriy chipta',cap);
  el('span',active?statusNames[active.status]:'Tayyor',cap).className='status-badge '+(active?.status||'ready');
  el('div',active?(active.label||number(active.number)):'—',current).className='number';
  el('p',active?(state.services.find(s=>s.id===active.service)?.name||'Xizmat'):'Keyingi chiptani chaqirishingiz mumkin',current).className='current-service';
  const department=choice(current,'Chaqirish uchun bo‘lim',[['','Barcha bo‘limlar'],...state.services.map(s=>[s.id,s.name])],operatorDepartment);department.parentElement.className='operator-filter';department.onchange=()=>{operatorDepartment=department.value};
  const actions=el('div',undefined,current);actions.className='ticket-actions';
  for(const [op,label,enabled] of [['next','Keyingisini chaqirish',!active],['recall','Qayta chaqirish',!!active],['start','Xizmatni boshlash',active?.status==='called'],['finish','Yakunlash',active?.status==='serving'],['absent','Kelmadi',active?.status==='called']]){
    const b=button(label,async()=>{await api('action',{action:op,ticket:active?.id,service:op==='next'&&operatorDepartment?Number(operatorDepartment):undefined});await staffData(await api('work'))},actions);b.disabled=!enabled;b.className='action-'+op;b.prepend(icon(op));
  }
  if(active){const transfer=el('div',undefined,current);transfer.className='transfer-box';
    const destination=choice(transfer,'Boshqa xizmatga yo‘naltirish',state.services.map(s=>[s.id,s.name]),active.service);
    const send=button('Yo‘naltirish',async()=>{await api('action',{action:'transfer',ticket:active.id,service:Number(destination.value)});await staffData(await api('work'))},transfer);send.className='secondary';send.prepend(icon('arrow'));
  }
  const queue=el('section',undefined,holder);queue.className='card waiting-card';
  const title=el('div',undefined,queue);title.className='queue-title';el('h3','Kutayotganlar',title);el('span',String(waiting.length),title).className='count-badge';
  const table=el('table',undefined,queue);const head=el('tr',undefined,el('thead',undefined,table));['Chipta','Xizmat','Holat',''].forEach(t=>el('th',t,head));
  const body=el('tbody',undefined,table);for(const t of waiting){const row=el('tr',undefined,body);el('td',t.label||number(t.number),row).className='queue-number';el('td',state.services.find(s=>s.id===t.service)?.name||t.service,row);el('span',statusNames[t.status],el('td',undefined,row)).className='status-badge waiting';const call=button('Chaqirish',async()=>{await api('action',{action:'next',ticket:t.id});await staffData(await api('work'))},el('td',undefined,row));call.className='queue-call';call.disabled=!!active;}
  if(data.active_windows?.length){const other=el('div',undefined,queue);other.className='other-operators';el('h3','Boshqa oynalardagi chiptalar',other);for(const t of data.active_windows)el('span',t.window+'-oyna · '+t.label+' · '+(state.services.find(s=>s.id===t.service)?.name||''),other);}
  if(!waiting.length){const cell=el('td','Kutayotgan chiptalar yo‘q',el('tr',undefined,body));cell.colSpan=4;cell.className='empty-state';}
}

async function admin(){
  let data;try{data=await api('admin')}catch{login();return}
  heading('Administrator paneli');const menu=el('div');menu.className='admin-tabs';const panel=el('section');panel.id='admin-panel';
  for(const [key,label] of [['audio','Ovozlar'],['settings','Sozlamalar'],['services','Xizmatlar'],['windows','Oynalar'],['displays','Elektron tablolar'],['users','Xodimlar'],['reports','Hisobotlar']]){const tab=button(label,async()=>{menu.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));tab.classList.add('active');panel.replaceChildren();data=await api('admin');await adminSection(key,data,panel);},menu);tab.className='tab'+(key==='audio'?' active':'');tab.prepend(icon(key));}
  const exit=button('Chiqish',async()=>{await api('logout',{});login()},menu);exit.className='ghost admin-exit';exit.prepend(icon('logout'));
  await audioAdmin(panel);
}
async function adminSection(key,data,panel){
  if(key==='audio')return audioAdmin(panel);
  if(key==='settings'){
    const f=el('form',undefined,panel);f.className='card form-grid settings-form';el('h2','Universitet va tizim sozlamalari',f);const c=data.settings;
    const fields={university:field(f,'Universitet nomi','text',c.university),open:field(f,'Ish boshlanishi','time',c.open),close:field(f,'Ish tugashi','time',c.close),printer_name:field(f,'Windows printer nomi','text',c.printer_name),paper_width_mm:field(f,'Qog‘oz kengligi (mm)','number',c.paper_width_mm),idle_seconds:field(f,'Bosh sahifaga qaytish (soniya)','number',c.idle_seconds),tv_rows:field(f,'TVda chaqiruvlar soni','number',c.tv_rows)};
    const serviceCodes=field(f,'Bo‘lim harflari','text',(data.services||[]).map(s=>s.prefix).join(' / '));serviceCodes.readOnly=true;
    const numbering=choice(f,'Raqamlash',[['daily','Har kuni yangidan'],['continuous','Uzluksiz']],c.daily_reset?'daily':'continuous');
    const printer=choice(f,'Printer rejimi',[['html','Brauzer / PDF sinov rejimi'],['windows','Windows drayveri orqali dialogsiz']],c.printer_mode);
    el('p','Har bir bo‘limning harfini Xizmatlar bo‘limida o‘zgartiring.',f);
    const days=el('fieldset',undefined,f);el('legend','Ish kunlari',days);const selected=[];
    ['Dushanba','Seshanba','Chorshanba','Payshanba','Juma','Shanba','Yakshanba'].forEach((name,i)=>{const box=field(days,name,'checkbox');box.checked=c.weekdays.includes(i);selected.push(box)});
    submitForm(f,async()=>{const body={};for(const [k,input] of Object.entries(fields))body[k]=input.type==='number'?Number(input.value):input.value;
      body.daily_reset=numbering.value==='daily';body.printer_mode=printer.value;body.weekdays=selected.flatMap((v,i)=>v.checked?[i]:[]);await api('settings',body);await refresh();});
    const diagnostics=el('section',undefined,panel);diagnostics.className='card branding-card';el('h2','Printer diagnostikasi',diagnostics);
    const printerList=choice(diagnostics,'Aniqlangan Windows printerlari',[[c.printer_name,c.printer_name||'Tanlang']],c.printer_name);
    printerList.onchange=()=>{fields.printer_name.value=printerList.value;printer.value='windows'};
    printerList.classList.add('technical');
    const info=el('p','Diagnostika yuklanmoqda…',diagnostics);info.className='technical';info.setAttribute('role','status');
    const jobs=el('div',undefined,diagnostics);let diagnosticRequest=null;
    async function inspectPrinter(){
      const d=await api('printer');printerList.replaceChildren();
      for(const item of d.printers||[]){const option=el('option',item.name+' · '+(item.driver||'')+' · '+(item.port||''),printerList);option.value=item.name;option.selected=item.name===fields.printer_name.value;}
      if(![...printerList.options].some(o=>o.value===fields.printer_name.value)){const o=el('option',fields.printer_name.value||'Printer topilmadi',printerList);o.value=fields.printer_name.value;o.selected=true;}
      info.textContent=d.error||('Windows hisobi: '+d.account+' · Spooler: '+d.spooler+'. Printed — Windows navbatiga qabul qilindi; haqiqiy qog‘oz chiqishi alohida tekshiriladi.');
      jobs.replaceChildren();
      diagnosticRequest=d.tests?.length&&['pending','printing'].includes(d.tests[0].status)?d.tests[0].request:null;
      for(const job of d.tests||[]){el('p','Sinov #'+job.id+': '+job.status+(job.error?' — '+job.error:''),jobs);}
      for(const job of d.jobs||[]){const row=el('p',job.label+' · '+job.status+(job.error?' — '+job.error:''),jobs);if(!['pending','printing'].includes(job.status))button('Shu chiptani qayta chop etish',async()=>{if(!confirm('Qog‘ozni tekshiring. Shu chiptani qayta chop etasizmi?'))return;await api('print',{request:job.ticket_request,previous_job:job.id,attempt:newRequest()});await inspectPrinter()},row);}
    }
    button('Printerlarni yangilash',inspectPrinter,diagnostics);
    button('Sinov cheki — navbat raqamisiz',async()=>{diagnosticRequest=diagnosticRequest||newRequest();await api('printer/test',{request:diagnosticRequest});await inspectPrinter()},diagnostics);
    inspectPrinter().catch(error=>{info.textContent=error.message});
    const brand=el('section',undefined,panel);brand.className='card branding-card';el('h2','Universitet logotipi',brand);
    const row=el('div',undefined,brand);row.className='branding-row';const preview=el('div',undefined,row);preview.className='logo-preview';const mark=el('img',undefined,preview);mark.src='/logo';mark.alt='Universitet logotipi';el('span',state.university,preview);
    const logoForm=el('form',undefined,row);logoForm.className='logo-form';const file=field(logoForm,'PNG yoki JPEG, 2 MB gacha','file');file.accept='.png,.jpg,.jpeg';file.required=true;
    submitForm(logoForm,async()=>{const image=file.files[0];if(image.size>2*1024*1024)throw Error('Rasm 2 MB dan oshmasin');await api('logo',{content:await readBase64(image)});location.reload()});

  }
  if(key==='services'){
    el('h2','Xizmatlar',panel);
    for(const s of [...data.services,{id:null,name:'',name_en:'',name_ru:'',enabled:1}]){
      const f=el('form',undefined,panel);f.className='card form-grid';el('h3',s.id?'Xizmat '+s.id:'Yangi xizmat',f);
      const prefix=field(f,'Bo‘lim harfi (A–Z)','text',s.prefix||'');prefix.maxLength=3;prefix.pattern='[A-Z]{1,3}';prefix.required=true;prefix.oninput=()=>{prefix.value=prefix.value.toUpperCase()};
      const uz=field(f,'Nomi — o‘zbek lotin','text',s.name),en=field(f,'Nomi — inglizcha','text',s.name_en),ru=field(f,'Nomi — ruscha','text',s.name_ru),on=field(f,'Faol','checkbox');on.checked=!!s.enabled;
      submitForm(f,()=>api('services',{id:s.id,prefix:prefix.value.trim().toUpperCase(),name:uz.value,name_en:en.value,name_ru:ru.value,enabled:on.checked}));
    }
  }
  if(key==='windows'){
    el('h2','Xizmat oynalari',panel);
    for(const w of [...data.windows,{id:'',name:'',enabled:1}]){const f=el('form',undefined,panel);f.className='card form-grid';const id=field(f,'Oyna raqami','number',w.id);id.readOnly=!!w.id;const name=field(f,'Oyna nomi','text',w.name),on=field(f,'Faol','checkbox');on.checked=!!w.enabled;submitForm(f,()=>api('windows',{id:Number(id.value),name:name.value,enabled:on.checked}));}
  }
  if(key==='users'){
    el('h2','Xodimlar va ruxsatlar',panel);
    for(const u of [...data.users,{name:'',role:'staff',window:1,services:[],enabled:1}]){
      const f=el('form',undefined,panel);f.className='card form-grid';el('h3',u.name||'Yangi xodim',f).className=u.name?'technical':'';
      const name=field(f,'Login','text',u.name);name.readOnly=!!u.name;
      const pass=field(f,u.name?'Yangi parol (o‘zgarmasa bo‘sh qoldiring)':'Parol (kamida 12 belgi)','password');pass.autocomplete='new-password';pass.required=!u.name;
      const role=choice(f,'Rol',[['staff','Xodim'],['admin','Administrator']],u.role);
      const window=choice(f,'Biriktirilgan oyna',data.windows.map(w=>[w.id,w.name]),u.window);
      const on=field(f,'Faol','checkbox');on.checked=!!u.enabled;
      el('p','Har bir operator barcha bo‘limlarni ko‘radi va chaqira oladi.',f).className='operator-access-note';
      submitForm(f,()=>api(u.name?'users/update':'users',{name:name.value,password:pass.value,role:role.value,window:Number(window.value),enabled:on.checked}));

    }
  }
  if(key==='displays'){
    el('h2','Elektron tablolar',panel);
    el('p','Hozir faqat apparatsiz sinov ishlaydi. Haqiqiy LED protokoli tasdiqlanmagan; COM/IP/agentga buyruq yuborilmaydi.',panel);
    const d=await api('displays');
    el('p','Windows portlari: '+(d.discovery.serial_ports.join(', ')||'Topilmadi')+'. Port topilishi LED aniqlanganini bildirmaydi.',panel).className='technical';
    const reload=async()=>{panel.replaceChildren();await adminSection('displays',await api('admin'),panel)};
    for(const w of data.windows){
      const saved=d.devices.find(v=>v.window===w.id);
      const f=el('form',undefined,panel);f.className='card form-grid';el('h3',w.id+'-oyna',f);
      el('p',!saved?'Sozlanmagan':saved.status==='simulation'?'Sinov rejimi — haqiqiy qurilma ulanmagan':saved.status==='disabled'?'O‘chirilgan':'Bloklangan — protokol tasdiqlanmagan',f);
      const address=field(f,'Qurilma ID manzili','text',saved?.device_address||String(w.id));address.maxLength=64;
      const transport=choice(f,'Ulanish turi',[['mock','Apparatsiz sinov'],['serial','COM — bloklangan'],['tcp','IP — bloklangan'],['agent','Operator agenti — bloklangan']],saved?.transport||'mock');
      const endpoint=field(f,'COM port / IP / agent manzili','text',saved?.endpoint||'');endpoint.maxLength=200;endpoint.className='technical';
      const on=field(f,'Faol','checkbox');on.checked=!!saved?.enabled;
      submitForm(f,async()=>{await api('displays',{window:w.id,device_address:address.value,transport:transport.value,endpoint:endpoint.value,enabled:on.checked});await reload()});
      if(saved){
        el('p','Oxirgi sinov qiymati: '+(saved.last_value??'—'),f).className='technical';
        const value=field(f,'Sinov raqami','text','A025');value.maxLength=12;
        button('Test raqam yuborish',async()=>{await api('displays/command',{device:saved.id,operation:'show',value:value.value});await reload()},f);
        button('Tabloni tozalash',async()=>{await api('displays/command',{device:saved.id,operation:'clear'});await reload()},f);
      }
    }
    const log=el('section',undefined,panel);log.className='card';el('h3','Tablo vazifalari',log);
    for(const j of d.jobs)el('p','#'+j.id+' · '+j.operation+' · '+j.value+' · '+j.status+(j.error?' — '+j.error:''),log).className='technical';
    button('Holatni yangilash',reload,panel);
  }
  if(key==='reports'){
    el('h2','Hisobotlar',panel);const f=el('form',undefined,panel);f.className='report-filters';
    const parts=Object.fromEntries(new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Tashkent',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()).map(p=>[p.type,p.value]));const today=parts.year+'-'+parts.month+'-'+parts.day;
    const start=field(f,'Boshlanish sanasi','date',today),end=field(f,'Tugash sanasi','date',today);
    const bar=el('div',undefined,panel);bar.className='report-downloads';const links=[];
    for(const [format,label] of [['xlsx','Excel (.xlsx)'],['docx','Word (.docx)'],['pdf','PDF']]){const a=el('a',label,bar);a.className='export-button export-'+format;a.download='';a.dataset.format=format;a.setAttribute('aria-disabled','true');a.onclick=e=>{if(a.getAttribute('aria-disabled')==='true')e.preventDefault()};a.prepend(icon('reports'));links.push(a);}
    const hint=el('p','Sana oralig‘ini tanlang va hisobotni ko‘rsating. Keyin kerakli formatni yuklab oling.',panel);hint.className='report-hint';
    const result=el('div',undefined,panel);result.className='report-preview';
    function invalidate(){links.forEach(a=>a.setAttribute('aria-disabled','true'));}
    start.oninput=invalidate;end.oninput=invalidate;
    const show=async()=>{
      const r=await api('reports?start='+start.value+'&end='+end.value);result.replaceChildren();
      const kpis=el('div',undefined,result);kpis.className='report-kpis';
      for(const [label,value] of [['Chiqarilgan chiptalar',r.issued],['Jami xizmat ko‘rsatilgan',r.served],['Kelmaganlar',r.absent],['Hozir kutayotganlar',r.waiting],['O‘rtacha kutish (minut)',r.average_wait_minutes??'—'],['O‘rtacha xizmat (minut)',r.average_service_minutes??'—']]){const card=el('div',undefined,kpis);el('span',label,card);el('strong',String(value),card);}
      for(const [group,label] of [['services','Bo‘limlar kesimida'],['employees','Operatorlar kesimida']]){
        const card=el('section',undefined,result);card.className='card report-table';el('h3',label,card);const table=el('table',undefined,card);const head=el('tr',undefined,el('thead',undefined,table));['Nomi','Chiqarilgan','Jami xizmat ko‘rsatilgan','Kelmagan','O‘rt. kutish (min)','O‘rt. xizmat (min)'].forEach(t=>el('th',t,head));const body=el('tbody',undefined,table);
        for(const [key,b] of Object.entries(r[group])){const row=el('tr',undefined,body);const name=group==='services'?data.services.find(s=>s.id===Number(key))?.name||key:key==='unassigned'?'Biriktirilmagan':key;[name,b.issued,b.done,b.absent,b.average_wait_minutes??'—',b.average_service_minutes??'—'].forEach((v,i)=>{const td=el('td',String(v),row);if(i===0&&group==='employees')td.className='technical'});}
        if(!Object.keys(r[group]).length){const cell=el('td','Bu davr uchun ma’lumot yo‘q',el('tr',undefined,body));cell.colSpan=6;}
      }
      links.forEach(a=>{a.href='/api/reports/export?format='+a.dataset.format+'&start='+encodeURIComponent(start.value)+'&end='+encodeURIComponent(end.value);a.setAttribute('aria-disabled','false');});
      hint.textContent='Davr: '+start.value+' — '+end.value+'. Kutish va xizmat vaqti minutda. Jami xizmat — yakunlangan chiptalar. Barcha formatlarda bir xil ma’lumot yuklanadi.';
    };
    submitForm(f,show);f.querySelector('button[type=submit]').textContent='Hisobotni ko‘rsatish';await show();
  }

}
let soundStatus='Ovoz o‘chirilgan',callCursor=null,pollingCalls=false,audioFiles={},audioMode='recorded',voiceURI='';
let autoAudioAttempted=false;
async function autoStartTVAudio(){
  if(location.pathname!=='/tv'||new URLSearchParams(location.search).get('autostart')!=='1'||autoAudioAttempted||recorded.missing().length)return;
  autoAudioAttempted=true;
  try{await recorded.enable()}catch(error){soundStatusUpdate('Avtomatik ovoz bloklandi. Kiosk brauzerida media autoplay ruxsatini yoqing. '+error.message)}
}
function soundStatusUpdate(text){soundStatus=text;const e=document.querySelector('#sound-status');if(e)e.textContent=text}
const recorded=new RecordedAnnouncer(window.Audio,soundStatusUpdate);
const announcer=new QueueAnnouncer(window.speechSynthesis,window.SpeechSynthesisUtterance,soundStatusUpdate);
function soundControls(){
  const details=el('details');details.open=!recorded.enabled&&!announcer.enabled;el('summary','Ovoz sozlamalari',details);const box=el('div',undefined,details);box.className='sound-controls';
  const mode=choice(box,'Ovoz manbasi',[['recorded','Yuklangan ovozlar'],['speech','Kompyuter lokal ovozi']],audioMode);
  mode.onchange=()=>{announcer.disable();recorded.disable();audioMode=mode.value;clear();tv()};
  const select=choice(box,'Lokal ovoz',announcer.voices().map(v=>[v.voiceURI,v.name+' ('+v.lang+')']),voiceURI);select.onchange=()=>{voiceURI=select.value};
  if(audioMode==='recorded')select.parentElement.hidden=true;
  button('Ovozni yoqish',async()=>{if(audioMode==='recorded'){recorded.configure(audioFiles,audioPrefixes());await recorded.enable();return;}
    const voice=announcer.voices().find(v=>v.voiceURI===select.value);if(!voice)throw Error('Lokal o‘zbek yoki rus ovozi topilmadi. Yuklangan ovozlardan foydalaning yoki Windows nutq paketini o‘rnating.');voiceURI=voice.voiceURI;announcer.enable(voice);},box);
  button('Ovozni sinash',()=>audioMode==='recorded'?recorded.test():announcer.test(),box);
  button('Ovozni o‘chirish',()=>{announcer.disable();recorded.disable()},box);
  el('p',soundStatus,box).id='sound-status';
  const missing=el('p','',box);missing.id='missing-voices';
}
function tv(){
  document.body.className='tv';
  let frame=document.querySelector('#tv-dashboard');
  if(!frame){
    clear();if(location.pathname==='/tv-audio'){soundControls();const enter=button('TV ekraniga o‘tish',()=>{history.replaceState(null,'','/tv');clear();tv()});enter.className='tv-enter';}
    frame=el('div');frame.id='tv-dashboard';frame.className='tv-dashboard';
    const hero=el('section',undefined,frame);hero.className='tv-hero';el('h2','Hozir chaqirilmoqda',hero).className='tv-section-title';
    el('div','—',hero).id='tv-current-number';el('div','',hero).id='tv-current-window';el('p','',hero).id='tv-current-service';
    const windows=el('section',undefined,frame);windows.className='tv-windows';el('h2','Xizmat oynalari',windows).className='tv-section-title';
    const table=el('table',undefined,windows);table.id='tv-calls';table.className='window-list';const head=el('tr',undefined,el('thead',undefined,table));el('th','OYNA',head);el('th','CHIPTA',head);el('tbody',undefined,table);
    const waiting=el('section',undefined,frame);waiting.className='tv-waiting';el('h2','Kutilayotgan navbatlar',waiting).className='tv-section-title';el('div',undefined,waiting).id='tv-waiting-list';
  }
  const latest=tvFlasher.current||state.calls[0];document.querySelector('#tv-current-number').textContent=latest?.label||'—';
  document.querySelector('#tv-current-window').textContent=latest?latest.window+'-oynaga marhamat':'Chaqiruvlar kutilmoqda…';
  document.querySelector('#tv-current-service').textContent=latest?(latest.service_name||state.services.find(s=>s.id===latest.service)?.name||''):'';
  const body=document.querySelector('#tv-calls tbody');body.replaceChildren();
  for(const call of state.window_calls.slice(0,5)){
    const row=el('tr',undefined,body);if(call.id===latest?.id)row.className='latest-window';el('td',call.window+'-oyna',row);el('td',call.label,row).className='technical';
  }
  if(!state.window_calls.length){const cell=el('td','Chaqiruvlar kutilmoqda…',el('tr',undefined,body));cell.colSpan=2;cell.className='tv-empty-call';}
  const queue=document.querySelector('#tv-waiting-list');queue.replaceChildren();
  for(const ticket of state.queue)el('span',ticket.label,queue).className='waiting-ticket technical';
  if(!state.queue.length)el('span','Kutayotgan chiptalar yo‘q',queue).className='empty-queue';
  const missing=document.querySelector('#missing-voices');if(missing)missing.textContent=audioMode==='recorded'&&recorded.missing().length?'Administrator panelida ovozlarni yuklang. Yetishmaydi: '+recorded.missing().join(', '):'';
}

const tvFlasher=new TVCallFlasher(()=>{if(isTV()&&state)tv()},()=>pulseTVNumbers([document.querySelector('#tv-current-number'),document.querySelector('#tv-current-window')]));

async function pollCalls(){
  if(pollingCalls)return;
  if(callCursor===null){callCursor=Math.max(0,...state.calls.map(c=>c.id));tvFlasher.lastId=callCursor;return}
  pollingCalls=true;
  try{let batch;do{batch=(await api('calls?after='+callCursor)).calls;announcer.enqueue(batch);recorded.enqueue(batch);tvFlasher.enqueue(batch);if(batch.length)callCursor=batch[batch.length-1].id;}while(batch.length===100)}finally{pollingCalls=false}
}
async function route(){if(isTV())tv();else if(location.pathname==='/admin')await admin();else if(location.pathname==='/staff')await staff();else terminal()}
async function refresh(){
  try{state=await api('state');updateBrand();document.body.dataset.connection='online';document.querySelector('#connection').textContent='● Ulangan';
    if(isTV()){audioFiles=(await api('audio')).files;recorded.configure(audioFiles,audioPrefixes());const newest=Math.max(0,...state.calls.map(c=>c.id));if(callCursor!==null&&newest<callCursor){callCursor=newest;recorded.lastId=newest;announcer.seen.clear();tvFlasher.lastId=newest;tvFlasher.pending=[];}await pollCalls();tv();await autoStartTVAudio()}
    if(!started){started=true;await route()}
    if(location.pathname==='/staff'&&document.querySelector('#staff-data')&&!document.activeElement?.matches('select,button'))try{await staffData(await api('work'))}catch{login()}
    return true;
  }catch{document.body.dataset.connection='offline';document.querySelector('#connection').textContent='● Aloqa uzildi. Qayta ulanmoqda…';return false}
}
if(window.speechSynthesis)window.speechSynthesis.addEventListener('voiceschanged',()=>{if(location.pathname==='/tv-audio'&&state&&!tvFlasher.running){clear();tv()}});
let refreshBusy=false;async function tick(){if(refreshBusy)return;refreshBusy=true;try{await refresh()}finally{refreshBusy=false}}tick();setInterval(tick,1500);
function updateClock(){const clock=document.querySelector('#clock');clock.replaceChildren();const now=new Date();el('span',now.toLocaleTimeString('uz-UZ',{timeZone:'Asia/Tashkent',hour:'2-digit',minute:'2-digit'}),clock).className='clock-time';const parts=Object.fromEntries(new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Tashkent',day:'numeric',month:'numeric',year:'numeric'}).formatToParts(now).map(p=>[p.type,p.value]));const months=['yanvar','fevral','mart','aprel','may','iyun','iyul','avgust','sentabr','oktabr','noyabr','dekabr'];el('span',parts.day+' '+months[Number(parts.month)-1]+' '+parts.year,clock).className='clock-date';}updateClock();setInterval(updateClock,1000);
let idle;function resetIdle(){clearTimeout(idle);idle=setTimeout(()=>{if(location.pathname==='/'&&!busy&&!recovered()){terminal()}},(state?.settings.idle_seconds||60)*1000)}document.addEventListener('pointerdown',resetIdle);resetIdle();
const logo=document.querySelector('.seal');const image=new Image();image.alt='Universitet logotipi';image.onload=()=>{logo.replaceChildren(image);logo.classList.toggle('has-logo',!!state?.custom_logo)};image.src='/logo';
function readBase64(file){return new Promise((resolve,reject)=>{const r=new FileReader();r.onerror=()=>reject(Error('Fayl o‘qilmadi'));r.onload=()=>resolve(r.result.split(',')[1]);r.readAsDataURL(file)})}
async function audioAdmin(parent=main){
  const card=el('section',undefined,parent);card.className='card';el('h2','Ovoz fayllarini yuklash',card);const tvLink=el('a','TV ovozini sozlash',card);tvLink.href='/tv-audio';tvLink.target='_blank';tvLink.rel='noopener';tvLink.className='text-link';tvLink.append(icon('arrow'));
  el('p','sounds.rar ni kompyuteringizda oching. Ichidagi WAV yoki MP3 fayllarni bu yerda bittadan tanlang (8 MB gacha). Har yozuvni tegishli belgi bilan saqlang.',card);
  const form=el('form',undefined,card);form.className='audio-upload-form';
  const slot=el('select',undefined,form);slot.setAttribute('aria-label','Ovoz vazifasi');
  const slots=[['attention','Diqqat (ixtiyoriy)'],['ticket','Chipta so‘zi'],...audioPrefixes().map(p=>['prefix_'+p,p+' harfi']),['window','Oyna so‘zi'],...Array.from({length:10},(_,n)=>['digit_'+n,n+' raqami'])];
  for(const [value,name] of slots){const option=el('option',name,slot);option.value=value;}
  const custom=el('input',undefined,form);custom.placeholder='Ixtiyoriy: window_1 yoki number_123';custom.setAttribute('aria-label','Maxsus ovoz belgisi');
  const file=el('input',undefined,form);file.type='file';file.accept='.wav,.mp3,audio/wav,audio/mpeg';file.required=true;file.setAttribute('aria-label','Ovoz fayli');decorateFile(file);
  const label=el('label',undefined,form);const rights=el('input',undefined,label);rights.type='checkbox';rights.required=true;label.append('Ushbu ovozlardan foydalanish huquqim bor');
  const submit=el('button','Ovozni yuklash',form);submit.type='submit';
  const feedback=el('p','',card);feedback.setAttribute('role','status');
  const list=el('div',undefined,card);
  async function render(){
    list.replaceChildren();const files=(await api('audio')).files;
    recorded.configure(files,audioPrefixes());const required=el('section',undefined,list);required.className='audio-requirements'+(recorded.missing().length?'':' complete');el('h3',recorded.missing().length?'Yetishmayotgan asosiy ovozlar':'Ovoz to‘plami tayyor',required);const chips=el('div',undefined,required);chips.className='audio-chips';for(const key of recorded.missing())el('span',/^digit_[0-9]$/.test(key)?key.slice(6):(slots.find(s=>s[0]===key)?.[1]||key),chips);
    for(const [key,entry] of Object.entries(files)){
      const row=el('div',undefined,list);row.className='audio-row';el('span',key+' — '+entry.name,row).className='technical';
      const player=el('audio',undefined,row);player.controls=true;player.preload='none';player.src=entry.url;
      button('O‘chirish',async()=>{if(confirm(key+' ovozi o‘chirilsinmi?')){await api('audio/delete',{slot:key});await render()}},row);
    }
  }
  form.onsubmit=async e=>{e.preventDefault();submit.disabled=true;try{
    const chosen=file.files[0];if(!chosen||chosen.size>8*1024*1024)throw Error('Fayl 8 MB dan oshmasin');
    feedback.textContent='Yuklanmoqda…';await api('audio/upload',{slot:custom.value.trim()||slot.value,name:chosen.name,content:await readBase64(chosen),rights_confirmed:rights.checked});
    feedback.textContent='Saqlandi. TVdagi «Ovozni sinash» tugmasi orqali tekshiring.';file.value='';file.resetLabel();await render();
  }catch(e){feedback.textContent=e.message}finally{submit.disabled=false}};
  await render();
}

document.addEventListener('pointerdown',async()=>{
  if(location.pathname!=='/tv'||!state||recorded.enabled||announcer.enabled)return;
  try{
    recorded.configure(audioFiles,audioPrefixes());
    if(!recorded.missing().length){await recorded.enable();return;}
    const voices=announcer.voices();const voice=voices.find(v=>/^uz/i.test(v.lang))||voices[0];
    if(voice)announcer.enable(voice);
  }catch(error){soundStatusUpdate(error.message);}
});

for(const link of document.querySelectorAll('nav a'))if(link.getAttribute('href')===location.pathname)link.setAttribute('aria-current','page');
