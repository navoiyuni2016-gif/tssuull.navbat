"""Independent LED outbox with simulation and explicitly configured raw profiles.

No vendor DLL or guessed protocol is used. COM/TCP frames come only from a
complete administrator-defined HEX profile; incomplete profiles cannot send.
"""
import datetime as dt
import logging
import json
import uuid
import os
import threading

LOG=logging.getLogger('navbat')
TRANSPORTS=('mock','serial','tcp','agent')
UNVERIFIED='LED protokoli tasdiqlanmagan. Qurilmaga buyruq yuborilmadi.'

def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()

def migrate(c):
    c.executescript('''
    CREATE TABLE IF NOT EXISTS display_devices(
      id INTEGER PRIMARY KEY, window INTEGER NOT NULL UNIQUE REFERENCES windows(id),
      device_address TEXT NOT NULL, transport TEXT NOT NULL, endpoint TEXT NOT NULL,
      enabled INTEGER NOT NULL DEFAULT 1, last_value TEXT, updated TEXT);
    CREATE TABLE IF NOT EXISTS display_jobs(
      id INTEGER PRIMARY KEY, device INTEGER NOT NULL REFERENCES display_devices(id),
      event INTEGER REFERENCES events(id), operation TEXT NOT NULL, value TEXT NOT NULL,
      status TEXT NOT NULL, created TEXT NOT NULL, finished TEXT, error TEXT,
      UNIQUE(device,event));
    CREATE UNIQUE INDEX IF NOT EXISTS display_device_address ON display_devices(transport,endpoint,device_address);
    ''')
    if 'profile' not in {r[1] for r in c.execute('PRAGMA table_info(display_devices)')}:
        c.execute("ALTER TABLE display_devices ADD COLUMN profile TEXT NOT NULL DEFAULT '{}'")

def validate_profile(value):
    if not isinstance(value,dict):raise ValueError('Tablo parametrlari obyekt bo‘lsin')
    fields={'baud_rate','data_bits','parity','stop_bits','segments','timeout_ms','tcp_port','model','protocol_note','protocol','show_template','clear_template','checksum_start'}
    if set(value)-fields:raise ValueError('Nomaʼlum tablo parametri')
    for key,low,high in [('baud_rate',50,4000000),('data_bits',5,8),('segments',1,16),('timeout_ms',100,60000),('tcp_port',1,65535),('checksum_start',0,511)]:
        item=value.get(key)
        if item is not None and (type(item) is not int or not low<=item<=high):raise ValueError(key+' qiymati noto‘g‘ri')
    if value.get('parity','') not in ('','N','E','O','M','S'):raise ValueError('Parity: N, E, O, M yoki S')
    if value.get('stop_bits','') not in ('','1','1.5','2'):raise ValueError('Stop bits: 1, 1.5 yoki 2')
    if value.get('protocol','') not in ('','manual_hex'):raise ValueError('Protokol: manual_hex yoki aniqlanmagan')
    for key,limit in [('model',200),('protocol_note',1000),('show_template',2000),('clear_template',2000)]:
        item=value.get(key,'')
        if not isinstance(item,str) or len(item)>limit or any(ord(ch)<32 and ch not in '\n\r\t' for ch in item):raise ValueError(key+' matni noto‘g‘ri')
    return dict(value)

def export_profile(c):
    return {'version':1,'devices':[{**{key:row[key] for key in ('window','device_address','transport','endpoint')},'enabled':bool(row['enabled']),'profile':json.loads(row['profile'])} for row in c.execute('SELECT * FROM display_devices ORDER BY window')]}

def import_profile(c,document):
    if not isinstance(document,dict) or type(document.get('version')) is not int or document['version']!=1 or set(document)!={'version','devices'}:raise ValueError('Tablo sozlamasi: version=1 kerak')
    devices=document['devices']
    if not isinstance(devices,list) or not 1<=len(devices)<=100 or any(not isinstance(d,dict) for d in devices):raise ValueError('1–100 ta tablo sozlamasi kerak')
    windows=[d.get('window') for d in devices]
    if any(type(n) is not int for n in windows) or len(set(windows))!=len(windows):raise ValueError('Oyna raqamlari takrorlanmasin')
    allowed={'window','device_address','transport','endpoint','enabled','profile'}
    if any(set(d)!=allowed for d in devices):raise ValueError('Tablo faylining maydonlari noto‘g‘ri')
    # A savepoint makes batches atomic even for standalone adapter callers.
    c.execute('SAVEPOINT display_profile_import')
    try:
        # Free unique addresses only inside this transaction, so IDs can be swapped.
        temporary='import-'+uuid.uuid4().hex
        for n in windows:c.execute('UPDATE display_devices SET transport=? WHERE window=?',(temporary+'-'+str(n),n))
        for device in devices:save(c,device)
    except Exception:
        c.execute('ROLLBACK TO display_profile_import');c.execute('RELEASE display_profile_import');raise
    c.execute('RELEASE display_profile_import')

def discover():
    ports=[];error=None
    if os.name=='nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'HARDWARE\DEVICEMAP\SERIALCOMM') as key:
                index=0
                while True:
                    try:ports.append(str(winreg.EnumValue(key,index)[1]));index+=1
                    except OSError:break
        except OSError as exc:error=str(exc)
    return {'serial_ports':sorted(set(ports)),'error':error,'devices_verified':False,
            'note':'Faqat Windows port nomlari. Port topilishi LED modeli/protokolini tasdiqlamaydi.'}

def save(c,body):
    window=body.get('window');transport=body.get('transport');enabled=body.get('enabled')
    if type(window) is not int or not c.execute('SELECT 1 FROM windows WHERE id=?',(window,)).fetchone():raise ValueError('Oynani to‘g‘ri tanlang')
    if transport not in TRANSPORTS:raise ValueError('Ulanish turi: mock, serial, tcp yoki agent')
    if type(enabled) is not bool:raise ValueError('Faollik qiymati noto‘g‘ri')
    address=body.get('device_address');endpoint=body.get('endpoint','')
    for value,limit in [(address,64),(endpoint,200)]:
        if not isinstance(value,str) or len(value)>limit or any(ord(ch)<32 for ch in value):raise ValueError('Qurilma manzili noto‘g‘ri')
    if not address.strip():raise ValueError('Qurilma ID manzili kerak')
    if transport!='mock' and not endpoint.strip():raise ValueError('COM / IP / agent manzili kerak')
    if c.execute("SELECT 1 FROM display_jobs WHERE device=(SELECT id FROM display_devices WHERE window=?) AND status='sending'",(window,)).fetchone():raise ValueError('Tablo yuborishi tugashini kuting, keyin sozlang')
    previous=c.execute('SELECT profile FROM display_devices WHERE window=?',(window,)).fetchone()
    profile=validate_profile(body['profile'] if 'profile' in body else json.loads(previous['profile']) if previous else {})
    if profile.get('protocol')=='manual_hex':
        import display_protocol
        display_protocol.prepare({'profile':profile,'transport':transport,'endpoint':endpoint.strip(),'device_address':address.strip(),'window':window},'A025','show')
    c.execute('''INSERT INTO display_devices(window,device_address,transport,endpoint,enabled,profile) VALUES (?,?,?,?,?,?)
      ON CONFLICT(window) DO UPDATE SET device_address=excluded.device_address,transport=excluded.transport,
      endpoint=excluded.endpoint,enabled=excluded.enabled,profile=excluded.profile,last_value=NULL,updated=NULL''',
      (window,address.strip(),transport,endpoint.strip(),enabled,json.dumps(profile,ensure_ascii=False)))
    # Never dispatch jobs with old settings after an administrator remaps a device.
    c.execute("UPDATE display_jobs SET status='cancelled',error='Qurilma sozlamasi o‘zgardi' WHERE device=(SELECT id FROM display_devices WHERE window=?) AND status='pending'",(window,))

def enqueue_event(c,event,window,operation,label):
    """Called inside the queue transaction; LED failure cannot undo the call/TV."""
    try:
        device=c.execute('SELECT * FROM display_devices WHERE window=? AND enabled=1',(window,)).fetchone()
        if not device:return
        clear=operation in ('finish','absent','transfer','refer_admin')
        if operation not in ('next','recall','finish','absent','transfer','refer_admin'):return
        simulated=device['transport']=='mock'
        configured=device['transport'] in ('serial','tcp') and json.loads(device['profile']).get('protocol')=='manual_hex'
        c.execute('INSERT OR IGNORE INTO display_jobs(device,event,operation,value,status,created,error) VALUES (?,?,?,?,?,?,?)',
            (device['id'],event,'clear' if clear else 'recall' if operation=='recall' else 'show','' if clear else label,
             'pending' if simulated or configured else 'blocked',stamp(),None if simulated or configured else UNVERIFIED))
        if not simulated and not configured:LOG.warning('LED window=%s: %s',window,UNVERIFIED)
    except Exception:LOG.exception('LED outbox yozilmadi; operator va TV davom etadi')

def command(c,body):
    if type(body.get('device')) is not int or body['device']<=0:raise ValueError('Qurilma ID raqami noto‘g‘ri')
    device=c.execute('SELECT * FROM display_devices WHERE id=? AND enabled=1',(body.get('device'),)).fetchone()
    if not device:raise ValueError('Faol tablo topilmadi')
    if device['transport']!='mock':
        import display_protocol
        item=dict(device);item['profile']=json.loads(device['profile']);display_protocol.prepare(item,body.get('value') or 'A025',body.get('operation'))
    operation=body.get('operation');value=body.get('value','')
    if operation not in ('show','clear'):raise ValueError('Amal: show yoki clear')
    if operation=='show' and (not isinstance(value,str) or not 1<=len(value)<=12 or not value.isascii() or not value.isalnum()):raise ValueError('Sinov belgisi: 1–12 lotin harfi yoki raqam')
    cursor=c.execute('INSERT INTO display_jobs(device,operation,value,status,created) VALUES (?,?,?,?,?)',
                     (device['id'],operation,'' if operation=='clear' else value,'pending',stamp()))
    return cursor.lastrowid

def state(c):
    devices=[]
    for row in c.execute('SELECT * FROM display_devices ORDER BY window'):
        item=dict(row);item['profile']=json.loads(row['profile']);item['status']='disabled' if not row['enabled'] else 'simulation' if row['transport']=='mock' else 'configured' if row['transport'] in ('serial','tcp') and item['profile'].get('protocol')=='manual_hex' else 'blocked'
        item['physical_verified']=False;devices.append(item)
    return {'devices':devices,'jobs':[dict(row) for row in c.execute('SELECT * FROM display_jobs ORDER BY id DESC LIMIT 30')],
            'discovery':discover(),'protocol_verified':False,'note':'HEX profilni administrator qo‘lda belgilaydi. sent — transportga yuborildi; fizik LED tasdig‘i emas.'}

class Worker:
    def __init__(self,connect,sender=None):
        self.connect=connect;self.stop=threading.Event();self.thread=None
        if sender is None:
            from display_protocol import send
            sender=send
        self.sender=sender
    def once(self):
        import display_protocol
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            job=c.execute("SELECT * FROM display_jobs WHERE status='pending' ORDER BY id LIMIT 1").fetchone()
            if not job:return False
            device=dict(c.execute('SELECT * FROM display_devices WHERE id=?',(job['device'],)).fetchone());device['profile']=json.loads(device['profile'])
            if not device['enabled']:
                c.execute("UPDATE display_jobs SET status='blocked',error=? WHERE id=?",('Tablo o‘chirilgan',job['id']));return True
            if device['transport']=='mock':
                c.execute('UPDATE display_devices SET last_value=?,updated=? WHERE id=?',(job['value'],stamp(),job['device']))
                c.execute("UPDATE display_jobs SET status='simulated',finished=? WHERE id=?",(stamp(),job['id']));return True
            try:payload=display_protocol.prepare(device,job['value'] or 'A025',job['operation'])
            except (ValueError,OverflowError,UnicodeError) as exc:
                c.execute("UPDATE display_jobs SET status='blocked',error=? WHERE id=?",(str(exc),job['id']));return True
            c.execute("UPDATE display_jobs SET status='sending' WHERE id=?",(job['id'],))
        status='sent';error=None
        try:self.sender(device,payload)
        except display_protocol.SendError as exc:status='uncertain' if exc.uncertain else 'failed';error=str(exc)
        except Exception as exc:status='uncertain';error=str(exc)
        if error:LOG.error('LED job=%s: %s',job['id'],error)
        with self.connect() as c:
            c.execute('UPDATE display_jobs SET status=?,finished=?,error=? WHERE id=?',(status,stamp(),error,job['id']))
            if status=='sent':c.execute('UPDATE display_devices SET last_value=?,updated=? WHERE id=?',(job['value'],stamp(),job['device']))
        return True
    def start(self):
        with self.connect() as c:c.execute("UPDATE display_jobs SET status='uncertain',error='Dastur yuborish paytida to‘xtagan; qayta yuborilmadi' WHERE status='sending'")
        def run():
            while not self.stop.is_set():
                try:
                    if self.once():continue
                except Exception:LOG.exception('LED sinov ishchisi xatosi')
                self.stop.wait(.5)
        self.thread=threading.Thread(target=run,name='led-simulator',daemon=True);self.thread.start()
    def close(self):
        self.stop.set()
        if self.thread:self.thread.join()
