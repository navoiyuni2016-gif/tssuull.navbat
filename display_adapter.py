"""Independent LED outbox. Only the hardware-free simulator is implemented.

No serial port, socket, vendor DLL, protocol guess or network discovery is used.
Real transports stay blocked until device documentation supplies a verified codec.
"""
import datetime as dt
import logging
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
    c.execute('''INSERT INTO display_devices(window,device_address,transport,endpoint,enabled) VALUES (?,?,?,?,?)
      ON CONFLICT(window) DO UPDATE SET device_address=excluded.device_address,transport=excluded.transport,
      endpoint=excluded.endpoint,enabled=excluded.enabled,last_value=NULL,updated=NULL''',
      (window,address.strip(),transport,endpoint.strip(),enabled))
    # Never dispatch jobs with old settings after an administrator remaps a device.
    c.execute("UPDATE display_jobs SET status='cancelled',error='Qurilma sozlamasi o‘zgardi' WHERE device=(SELECT id FROM display_devices WHERE window=?) AND status='pending'",(window,))

def enqueue_event(c,event,window,operation,label):
    """Called inside the queue transaction; LED failure cannot undo the call/TV."""
    try:
        device=c.execute('SELECT * FROM display_devices WHERE window=? AND enabled=1',(window,)).fetchone()
        if not device:return
        clear=operation in ('finish','absent','transfer')
        if operation not in ('next','recall','finish','absent','transfer'):return
        simulated=device['transport']=='mock'
        c.execute('INSERT OR IGNORE INTO display_jobs(device,event,operation,value,status,created,error) VALUES (?,?,?,?,?,?,?)',
            (device['id'],event,'clear' if clear else 'recall' if operation=='recall' else 'show','' if clear else label,
             'pending' if simulated else 'blocked',stamp(),None if simulated else UNVERIFIED))
        if not simulated:LOG.warning('LED window=%s: %s',window,UNVERIFIED)
    except Exception:LOG.exception('LED outbox yozilmadi; operator va TV davom etadi')

def command(c,body):
    if type(body.get('device')) is not int or body['device']<=0:raise ValueError('Qurilma ID raqami noto‘g‘ri')
    device=c.execute('SELECT * FROM display_devices WHERE id=? AND enabled=1',(body.get('device'),)).fetchone()
    if not device:raise ValueError('Faol tablo topilmadi')
    if device['transport']!='mock':raise ValueError(UNVERIFIED)
    operation=body.get('operation');value=body.get('value','')
    if operation not in ('show','clear'):raise ValueError('Amal: show yoki clear')
    if operation=='show' and (not isinstance(value,str) or not 1<=len(value)<=12 or not value.isascii() or not value.isalnum()):raise ValueError('Sinov belgisi: 1–12 lotin harfi yoki raqam')
    cursor=c.execute('INSERT INTO display_jobs(device,operation,value,status,created) VALUES (?,?,?,?,?)',
                     (device['id'],operation,'' if operation=='clear' else value,'pending',stamp()))
    return cursor.lastrowid

def state(c):
    devices=[]
    for row in c.execute('SELECT * FROM display_devices ORDER BY window'):
        item=dict(row);item['status']='disabled' if not row['enabled'] else 'simulation' if row['transport']=='mock' else 'blocked'
        item['physical_verified']=False;devices.append(item)
    return {'devices':devices,'jobs':[dict(row) for row in c.execute('SELECT * FROM display_jobs ORDER BY id DESC LIMIT 30')],
            'discovery':discover(),'protocol_verified':False,'note':UNVERIFIED}

class Worker:
    def __init__(self,connect):self.connect=connect;self.stop=threading.Event();self.thread=None
    def once(self):
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            job=c.execute("SELECT j.*,d.transport,d.enabled FROM display_jobs j JOIN display_devices d ON d.id=j.device WHERE j.status='pending' ORDER BY j.id LIMIT 1").fetchone()
            if not job:return False
            if not job['enabled'] or job['transport']!='mock':
                c.execute("UPDATE display_jobs SET status='blocked',error=? WHERE id=?",(UNVERIFIED,job['id']));return True
            # Simulator updates SQLite only. It never opens any physical transport.
            c.execute('UPDATE display_devices SET last_value=?,updated=? WHERE id=?',(job['value'],stamp(),job['device']))
            c.execute("UPDATE display_jobs SET status='simulated',finished=? WHERE id=?",(stamp(),job['id']))
            return True
    def start(self):
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
