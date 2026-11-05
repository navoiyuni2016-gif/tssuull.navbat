"""Independent, offline university queue server. Python 3.12+, standard library."""
import argparse
import subprocess
import datetime as dt
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3
import re
import audio_store
import management
import alphabet
import printer_adapter
import report_exports
import base64
import logging
from logging.handlers import RotatingFileHandler
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).parent
DATA = Path(os.environ.get('NAVBAT_DATA', ROOT / 'data'))
TZ = dt.timezone(dt.timedelta(hours=5))
NAMES = ['Talabalarga xizmat ko‘rsatish sektori', 'Ilmiy va innovatsion faoliyat bo‘yicha xizmat ko‘rsatish sektori', 'Xalqaro aloqalar va akademik mobillik bo‘yicha xizmat ko‘rsatish sektori', 'Marketing va amaliyotlarni tashkil etish', 'Buxgalteriya bo‘yicha xizmat ko‘rsatish sektori']
UNIVERSITY = 'Alisher Navoiy nomidagi Toshkent davlat o‘zbek tili va adabiyoti universiteti'

def connect():
    c = sqlite3.connect(DATA / 'queue.db', timeout=30)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c

def password(value, salt):
    return hashlib.pbkdf2_hmac('sha256', value.encode(), salt.encode(), 300000).hex()

def initialize(admin_password=None):
    DATA.mkdir(parents=True, exist_ok=True)
    with connect() as c:
        c.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS services(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS users(name TEXT PRIMARY KEY,salt TEXT NOT NULL,hash TEXT NOT NULL,role TEXT NOT NULL,window INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user TEXT NOT NULL REFERENCES users(name),expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY,day TEXT NOT NULL,number INTEGER NOT NULL,service INTEGER NOT NULL REFERENCES services(id),request TEXT UNIQUE NOT NULL,status TEXT NOT NULL DEFAULT 'waiting',window INTEGER,user TEXT,created TEXT NOT NULL,called TEXT,started TEXT,finished TEXT,UNIQUE(day,number));
        CREATE TABLE IF NOT EXISTS calls(id INTEGER PRIMARY KEY,ticket INTEGER NOT NULL REFERENCES tickets(id),window INTEGER NOT NULL,created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audio(slot TEXT PRIMARY KEY,name TEXT NOT NULL,mime TEXT NOT NULL,digest TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS branding(id INTEGER PRIMARY KEY CHECK(id=1),content BLOB NOT NULL,mime TEXT NOT NULL);
        ''')
        if not c.execute('SELECT 1 FROM services').fetchone():
            c.executemany('INSERT INTO services(name) VALUES (?)', [(alphabet.text(n),) for n in NAMES])
        if not c.execute('SELECT 1 FROM users').fetchone():
            if not admin_password or len(admin_password) < 12:
                raise ValueError('Administrator paroli kamida 12 belgi bo‘lsin')
            salt = secrets.token_hex(16)
            c.execute('INSERT INTO users(name,salt,hash,role,window) VALUES (?,?,?,?,?)', ('admin', salt, password(admin_password, salt), 'admin', 1))
        management.migrate(c)

def now():
    return dt.datetime.now(TZ).isoformat()

def issue(service, request, lang='uz'):
    if lang not in ('uz','ru','en'):
        raise ValueError('Til tanlovi noto‘g‘ri')
    if not isinstance(request, str) or not 16 <= len(request) <= 100:
        raise ValueError('Invalid request ID')
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        old = c.execute('SELECT * FROM tickets WHERE request=?', (request,)).fetchone()
        if old:
            if old['service'] != service:
                raise ValueError('Request ID belongs to another service')
            return dict(old)
        if not c.execute('SELECT 1 FROM services WHERE id=? AND enabled=1', (service,)).fetchone():
            raise ValueError('Xizmat topilmadi yoki faol emas')
        config = management.settings(c)
        current = dt.datetime.now(TZ)
        if current.weekday() not in config['weekdays'] or not config['open'] <= current.strftime('%H:%M') <= config['close']:
            raise ValueError('Hozir ish vaqti emas')
        stamp = now()
        day = stamp[:10]
        number = c.execute('SELECT coalesce(max(number),0)+1 FROM tickets'+(' WHERE day=?' if config['daily_reset'] else ''), (day,) if config['daily_reset'] else ()).fetchone()[0]
        ahead = c.execute("SELECT count(*) FROM tickets WHERE service=? AND status='waiting'", (service,)).fetchone()[0]
        label = config['prefix'] + str(number).zfill(3)
        cursor = c.execute('INSERT INTO tickets(day,number,service,request,created,label,ahead,lang) VALUES (?,?,?,?,?,?,?,?)', (day, number, service, request, stamp,label,ahead,lang))
        c.execute("INSERT INTO events(ticket,operation,service,created) VALUES (?,'issued',?,?)",(cursor.lastrowid,service,stamp))
        c.execute('INSERT INTO print_jobs(ticket,status,created) VALUES (?,?,?)',(cursor.lastrowid,'pending' if config['printer_mode']=='windows' else 'preview',stamp))
        return dict(c.execute('SELECT * FROM tickets WHERE id=?', (cursor.lastrowid,)).fetchone())

def action(user, operation, ticket=None, service=None):
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        window = user['window']
        permitted = management.allowed(c,user)
        active = c.execute("SELECT * FROM tickets WHERE window=? AND status IN ('called','serving')", (window,)).fetchone()
        if operation == 'next':
            if active:
                raise ValueError('Avval joriy chiptani yakunlang')
            if not c.execute('SELECT 1 FROM windows WHERE id=? AND enabled=1',(window,)).fetchone():
                raise ValueError('Xizmat oynasi faol emas')
            if ticket is not None and (type(ticket) is not int or ticket<=0):raise ValueError('Chipta raqami noto‘g‘ri')
            if service is not None and (type(service) is not int or service not in permitted):raise ValueError('Xizmatni to‘g‘ri tanlang')
            query="SELECT * FROM tickets WHERE status='waiting' AND service IN (SELECT value FROM json_each(?))"
            parameters=[json.dumps(permitted)]
            if ticket is not None:query+=' AND id=?';parameters.append(ticket)
            if service is not None:query+=' AND service=?';parameters.append(service)
            active=c.execute(query+' ORDER BY id LIMIT 1',parameters).fetchone()
            if active is None and ticket is not None:raise ValueError('Bu chipta allaqachon chaqirilgan yoki kutishda emas')
            if not active:
                return None
            c.execute("UPDATE tickets SET status='called',window=?,user=?,called=? WHERE id=?", (window,user['name'],now(),active['id']))
        else:
            if not active or active['id'] != ticket or active['user'] != user['name']:
                raise ValueError('Bu chipta sizga biriktirilmagan')
            if operation == 'transfer':
                if not c.execute('SELECT 1 FROM services WHERE id=? AND enabled=1',(service,)).fetchone():
                    raise ValueError('Yo‘naltiriladigan xizmatni tanlang')
                c.execute("UPDATE tickets SET service=?,status='waiting',window=NULL,user=NULL,called=NULL,started=NULL WHERE id=?",(service,ticket))
                c.execute("INSERT INTO events(ticket,operation,user,service,window,created) VALUES (?,'transfer',?,?,?,?)",(ticket,user['name'],service,window,now()))
                return dict(c.execute('SELECT * FROM tickets WHERE id=?',(ticket,)).fetchone())
            target = {'start': ('called','serving','started'), 'finish': ('serving','done','finished'), 'absent': ('called','absent','finished')}
            if operation in target:
                source, state, column = target[operation]
                if active['status'] != source:
                    raise ValueError('Bu holatda amal bajarilmaydi')
                c.execute(f'UPDATE tickets SET status=?,{column}=? WHERE id=?', (state,now(),ticket))
            elif operation != 'recall':
                raise ValueError('Noma’lum amal')
        if operation in ('next','recall'):
            c.execute('INSERT INTO calls(ticket,window,created,service) VALUES (?,?,?,?)', (active['id'],window,now(),active['service']))
        c.execute('INSERT INTO events(ticket,operation,user,service,window,created) VALUES (?,?,?,?,?,?)',(active['id'],operation,user['name'],active['service'],window,now()))
        return dict(c.execute('SELECT * FROM tickets WHERE id=?', (active['id'],)).fetchone())

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, status, value, cookie=None):
        if isinstance(value,dict) and 'error' in value:
            translations={'Login required':'Tizimga kiring','Invalid request ID':'So‘rov belgisi noto‘g‘ri','Request ID belongs to another service':'Bu so‘rov boshqa xizmatga tegishli','Invalid request size':'So‘rov hajmi noto‘g‘ri','JSON object required':'So‘rov JSON obyekt bo‘lishi kerak','Administrator login required':'Administrator sifatida kiring','Same-origin JSON required':'So‘rovni tizim sahifasidan yuboring','Not found':'Sahifa topilmadi','Audio not found':'Ovoz topilmadi','Invalid call cursor':'Chaqiruv belgisi noto‘g‘ri','Unknown setting':'Noma’lum sozlama'}
            value['error']=alphabet.text(translations.get(value['error'],value['error']))
        payload = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        if cookie:
            self.send_header('Set-Cookie',cookie)
        self.end_headers()
        self.wfile.write(payload)

    def user(self):
        cookie = SimpleCookie(self.headers.get('Cookie',''))
        token = cookie.get('session')
        if not token:
            return None
        with connect() as c:
            row = c.execute('SELECT users.* FROM sessions JOIN users ON users.name=sessions.user WHERE token=? AND expires>? AND users.enabled=1', (token.value,dt.datetime.now().timestamp())).fetchone()
            return dict(row) if row else None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/health':
            from desktop_runtime import instance_id
            return self.send(200,{'app':'toshdotau-navbat','instance':instance_id(DATA)})
        if parsed.path == '/api/reports/export':
            u=self.user()
            if not u or u['role']!='admin':return self.send(403,{'error':'Administrator sifatida kiring'})
            query=parse_qs(parsed.query);today=dt.datetime.now(TZ).date().isoformat()
            try:
                fmt=query.get('format',['pdf'])[0]
                if fmt not in report_exports.FORMATS:raise ValueError('Format: xlsx, docx yoki pdf')
                with connect() as c:data=report_exports.snapshot(c,query.get('start',[today])[0],query.get('end',[today])[0])
                payload,mime,filename=report_exports.render(data,fmt)
                return self.binary(payload,mime,filename)
            except ValueError as error:return self.send(400,{'error':str(error)})
        if parsed.path == '/background':
            for name,mime in (('campus-background.png','image/png'),('campus-background.jpg','image/jpeg'),('campus-background.jpeg','image/jpeg')):
                path=ROOT/'web'/'assets'/name
                if path.is_file():
                    return self.binary(path.read_bytes(),mime)
            return self.binary((ROOT/'web'/'assets'/'campus-pattern.svg').read_bytes(),'image/svg+xml')
        if parsed.path == '/logo':
            with connect() as c:
                row=c.execute('SELECT * FROM branding WHERE id=1').fetchone()
            if row:return self.binary(row['content'],row['mime'])
            logo=ROOT/'web'/'assets'/'university-logo.png'
            if logo.is_file():return self.binary(logo.read_bytes(),'image/png')
            return self.binary((ROOT/'web'/'assets'/'brand-mark.svg').read_bytes(),'image/svg+xml')
        if self.path == '/assets/brand-mark.svg':
            return self.binary((ROOT/'web'/'assets'/'brand-mark.svg').read_bytes(),'image/svg+xml')
        if self.path == '/assets/panel-pattern.svg':
            return self.binary((ROOT/'web'/'assets'/'panel-pattern.svg').read_bytes(),'image/svg+xml')
        if self.path == '/assets/campus-pattern.svg':
            return self.binary((ROOT/'web'/'assets'/'campus-pattern.svg').read_bytes(),'image/svg+xml')
        if parsed.path == '/receipt':
            query=parse_qs(parsed.query)
            with connect() as c:
                row=c.execute('SELECT tickets.*,services.name AS service_name,services.name_ru AS service_name_ru,services.name_en AS service_name_en FROM tickets JOIN services ON services.id=tickets.service WHERE request=?',(query.get('request',[''])[0],)).fetchone()
                if not row:return self.send(404,{'error':'Chipta topilmadi'})
                payload=printer_adapter.preview(row,printer_adapter.service_name(row),management.settings(c)['university'])
            return self.binary(payload.encode(),'text/html; charset=utf-8')
        if parsed.path in ('/api/admin','/api/reports'):
            u = self.user()
            if not u or u['role'] != 'admin':
                return self.send(403,{'error':'Administrator sifatida kiring'})
            with connect() as c:
                if parsed.path == '/api/reports':
                    query=parse_qs(parsed.query)
                    today=dt.datetime.now(TZ).date().isoformat()
                    try:
                        return self.send(200,management.report(c,query.get('start',[today])[0],query.get('end',[today])[0]))
                    except ValueError:
                        return self.send(400,{'error':'Sana YYYY-MM-DD shaklida bo‘lsin'})
                users=[]
                for row in c.execute('SELECT name,role,window,enabled FROM users'):
                    item=dict(row);item['services']=[r[0] for r in c.execute('SELECT service FROM permissions WHERE user=?',(row['name'],))];users.append(item)
                return self.send(200,{'settings':management.settings(c),'services':[dict(r) for r in c.execute('SELECT id,name,name_ru,name_en,enabled FROM services')],'windows':[dict(r) for r in c.execute('SELECT * FROM windows')],'users':users})
        if self.path == '/api/audio':
            with connect() as c:
                return self.send(200, {'files':audio_store.manifest(c)})
        if re.fullmatch(r'/audio/[0-9a-f]{64}', self.path):
            digest = self.path.rsplit('/',1)[1]
            with connect() as c:
                row = c.execute('SELECT mime FROM audio WHERE digest=?',(digest,)).fetchone()
            path = DATA / 'audio' / digest
            if not row or not path.is_file():
                return self.send(404, {'error':'Audio not found'})
            payload = path.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type',row['mime'])
            self.send_header('Content-Length',str(len(payload)))
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Cache-Control','public, max-age=31536000, immutable')
            self.end_headers()
            self.wfile.write(payload)
            return
        if urlparse(self.path).path == '/api/calls':
            try:
                after = int(parse_qs(urlparse(self.path).query).get('after', ['0'])[0])
                if after < 0:
                    raise ValueError()
            except ValueError:
                return self.send(400, {'error':'Invalid call cursor'})
            with connect() as c:
                rows = c.execute('SELECT calls.id,tickets.number,tickets.label,calls.service,services.name AS service_name,calls.window FROM calls JOIN tickets ON tickets.id=calls.ticket JOIN services ON services.id=calls.service WHERE calls.id>? ORDER BY calls.id LIMIT 100', (after,))
                return self.send(200, {'calls':[dict(r) for r in rows]})
        if self.path == '/api/state':
            with connect() as c:
                config=management.settings(c)
                calls = c.execute('SELECT calls.id,tickets.number,tickets.label,calls.service,services.name AS service_name,calls.window FROM calls JOIN tickets ON tickets.id=calls.ticket JOIN services ON services.id=calls.service ORDER BY calls.id DESC LIMIT ?', (config['tv_rows'],)).fetchall()
                queue=[dict(r) for r in c.execute("SELECT id,number,label,service FROM tickets WHERE status='waiting' ORDER BY id LIMIT 5")]
                window_calls=[dict(r) for r in c.execute("SELECT calls.id,tickets.label,tickets.number,calls.window,calls.service,services.name AS service_name FROM calls JOIN tickets ON tickets.id=calls.ticket JOIN services ON services.id=calls.service WHERE calls.id IN (SELECT max(id) FROM calls GROUP BY window) ORDER BY calls.window")]
                waiting = c.execute("SELECT count(*) FROM tickets WHERE status='waiting'").fetchone()[0]
                self.send(200,dict(university=config['university'],custom_background=any((ROOT/'web'/'assets'/name).is_file() for name in ('campus-background.png','campus-background.jpg','campus-background.jpeg')),custom_logo=bool(c.execute('SELECT 1 FROM branding WHERE id=1').fetchone()) or (ROOT/'web'/'assets'/'university-logo.png').is_file(),settings={k:config[k] for k in ('prefix','idle_seconds','tv_rows','printer_mode')},services=[dict(r) for r in c.execute('SELECT id,name,name_ru,name_en,enabled FROM services WHERE enabled=1')],calls=[dict(r) for r in calls],window_calls=window_calls,queue=queue,waiting=waiting))
            return
        if self.path == '/api/work':
            u = self.user()
            if not u:
                return self.send(401,{'error':'Login required'})
            with connect() as c:
                rows = c.execute("SELECT * FROM tickets WHERE (status='waiting' AND service IN (SELECT value FROM json_each(?))) OR (user=? AND status IN ('called','serving')) ORDER BY id", (json.dumps(management.allowed(c,u)),u['name']))
                tickets=[dict(r) for r in rows]
                busy=[dict(r) for r in c.execute("SELECT id,label,service,window,status FROM tickets WHERE status IN ('called','serving') AND user<>? ORDER BY window",(u['name'],))]
                return self.send(200,{'tickets':tickets,'active_windows':busy,'role':u['role'],'window':u['window']})
        path = {'/':'index.html','/staff':'index.html','/tv':'index.html','/tv-audio':'index.html','/admin':'index.html','/style.css':'style.css','/reference-theme.css':'reference-theme.css','/sample-match.css':'sample-match.css','/app.js':'app.js','/announcer.js':'announcer.js','/recordings.js':'recordings.js','/tv-flasher.js':'tv-flasher.js','/alphabet.js':'alphabet.js'}.get(parsed.path)
        if not path:
            return self.send(404,{'error':'Not found'})
        data = (ROOT/'web'/path).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type',{'html':'text/html; charset=utf-8','css':'text/css','js':'application/javascript'}[path.split('.')[-1]])
        self.send_header('Content-Security-Policy',"default-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.send_header('Content-Length',str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        # Same-origin JSON requests only; cross-origin forms cannot mutate state.
        origin = self.headers.get('Origin')
        if (origin and origin != 'http://' + self.headers.get('Host','')) or self.headers.get('Content-Type') != 'application/json':
            return self.send(403,{'error':'Same-origin JSON required'})
        try:
            if self.path in ('/api/audio/upload','/api/audio/delete','/api/logo','/api/settings','/api/services','/api/windows','/api/users/update'):
                u = self.user()
                if not u or u['role'] != 'admin':
                    return self.send(403,{'error':'Administrator login required'})
            size = int(self.headers.get('Content-Length',0))
            limit = 12 * 1024 * 1024 if self.path in ('/api/audio/upload','/api/logo') else 8192
            if not 0 < size <= limit:
                raise ValueError('Invalid request size')
            body = json.loads(self.rfile.read(size))
            if not isinstance(body,dict):
                raise ValueError('JSON object required')
            if self.path == '/api/logo':
                try:
                    payload=base64.b64decode(body['content'],validate=True)
                except (ValueError,TypeError):raise ValueError('Rasm o‘qilmadi')
                if not 16<=len(payload)<=2*1024*1024:raise ValueError('Logotip 2 MB gacha bo‘lsin')
                mime='image/png' if payload.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if payload.startswith(b'\xff\xd8\xff') else None
                if not mime:raise ValueError('PNG yoki JPEG rasm tanlang')
                with connect() as c:c.execute('INSERT OR REPLACE INTO branding VALUES (1,?,?)',(payload,mime))
                return self.send(200,{'ok':True})
            if self.path in ('/api/print','/api/print/status'):
                with connect() as c:
                    c.execute('BEGIN IMMEDIATE')
                    row=c.execute('SELECT * FROM tickets WHERE request=?',(body.get('request',''),)).fetchone()
                    if not row:raise ValueError('Chipta topilmadi')
                    job=c.execute('SELECT id,status,error FROM print_jobs WHERE ticket=? ORDER BY id DESC LIMIT 1',(row['id'],)).fetchone()
                    if self.path=='/api/print' and (not job or job['status'] not in ('pending','dispatching')):
                        config=management.settings(c)
                        c.execute('INSERT INTO print_jobs(ticket,status,created) VALUES (?,?,?)',(row['id'],'pending' if config['printer_mode']=='windows' else 'preview',now()))
                        job=c.execute('SELECT id,status,error FROM print_jobs WHERE ticket=? ORDER BY id DESC LIMIT 1',(row['id'],)).fetchone()
                return self.send(200,{'job':dict(job) if job else None})
            if self.path == '/api/audio/upload':
                with connect() as c:
                    result = audio_store.save(c,DATA/'audio',body)
                return self.send(200,result)
            if self.path == '/api/audio/delete':
                with connect() as c:
                    c.execute('DELETE FROM audio WHERE slot=?',(body['slot'],))
                return self.send(200,{'ok':True})
            if self.path == '/api/settings':
                with connect() as c:
                    result=management.save_settings(c,body)
                return self.send(200,result)
            if self.path == '/api/services':
                if isinstance(body.get('name'),str):body['name']=alphabet.text(body['name'])
                for key in ('name','name_en','name_ru'):
                    if not isinstance(body.get(key),str) or not 1<=len(body[key])<=300:
                        raise ValueError('Uch tildagi xizmat nomini kiriting')
                if type(body.get('enabled')) is not bool:
                    raise ValueError('Faollik qiymati noto‘g‘ri')
                with connect() as c:
                    if body.get('id'):
                        c.execute('UPDATE services SET name=?,name_en=?,name_ru=?,enabled=? WHERE id=?',(body['name'],body['name_en'],body['name_ru'],body['enabled'],int(body['id'])))
                    else:
                        c.execute('INSERT INTO services(name,name_en,name_ru,enabled) VALUES (?,?,?,?)',(body['name'],body['name_en'],body['name_ru'],body['enabled']))
                return self.send(200,{'ok':True})
            if self.path == '/api/windows':
                identifier=int(body['id'])
                if not 1<=identifier<=100 or not isinstance(body.get('name'),str) or not 1<=len(body['name'])<=100 or type(body.get('enabled')) is not bool:
                    raise ValueError('Oyna raqami 1–100 va nomini kiriting')
                with connect() as c:
                    c.execute('INSERT INTO windows VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,enabled=excluded.enabled',(identifier,body['name'],body['enabled']))
                return self.send(200,{'ok':True})
            if self.path == '/api/tickets':
                return self.send(200,issue(int(body['service']),body['request'],body.get('lang','uz')))
            if self.path == '/api/login':
                if not isinstance(body.get('name'),str) or not isinstance(body.get('password'),str):raise ValueError('Login va parolni kiriting')
                with connect() as c:
                    u = c.execute('SELECT * FROM users WHERE name=?',(body['name'],)).fetchone()
                    if not u or not u['enabled'] or not isinstance(body.get('password'),str) or not hmac.compare_digest(u['hash'],password(body['password'],u['salt'])):
                        return self.send(401,{'error':'Login yoki parol noto‘g‘ri'})
                    token = secrets.token_hex(32)
                    c.execute('INSERT INTO sessions VALUES (?,?,?)',(token,u['name'],dt.datetime.now().timestamp()+28800))
                return self.send(200,{'ok':True},f'session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800')
            u = self.user()
            if not u:
                return self.send(401,{'error':'Tizimga kiring'})
            if self.path == '/api/logout':
                cookie=SimpleCookie(self.headers.get('Cookie',''))
                with connect() as c:
                    c.execute('DELETE FROM sessions WHERE token=?',(cookie['session'].value,))
                return self.send(200,{'ok':True},'session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
            if self.path == '/api/action':
                return self.send(200,action(u,body['action'],body.get('ticket'),body.get('service')))
            if self.path in ('/api/users','/api/users/update') and u['role'] == 'admin':
                updating=self.path.endswith('/update')
                if body.get('role') not in ('admin','staff') or not isinstance(body.get('name'),str) or not re.fullmatch('[A-Za-z0-9_.-]{1,50}',body['name']) or not isinstance(body.get('password',''),str) or ((not updating or body.get('password')) and len(body.get('password',''))<12) or not 1<=int(body['window'])<=100 or type(body.get('enabled',True)) is not bool:
                    raise ValueError('Login, rol, oyna yoki parol noto‘g‘ri (kamida 12 belgi)')
                if body['name']==u['name'] and (body.get('enabled',True) is not True or body['role']!='admin'):
                    raise ValueError('O‘z administrator hisobingizni bloklay olmaysiz')
                salt = secrets.token_hex(16)
                with connect() as c:
                    if not c.execute('SELECT 1 FROM windows WHERE id=?',(int(body['window']),)).fetchone():raise ValueError('Oyna topilmadi')
                    services=[row[0] for row in c.execute('SELECT id FROM services')]
                    if not isinstance(services,list) or any(type(s) is not int or not c.execute('SELECT 1 FROM services WHERE id=?',(s,)).fetchone() for s in services):raise ValueError('Xizmat ruxsatlari noto‘g‘ri')
                    if updating:
                        existing=c.execute('SELECT * FROM users WHERE name=?',(body['name'],)).fetchone()
                        if not existing:raise ValueError('Xodim topilmadi')
                        if (int(body['window'])!=existing['window'] or not body.get('enabled',True)) and c.execute("SELECT 1 FROM tickets WHERE user=? AND status IN ('called','serving')",(body['name'],)).fetchone():raise ValueError('Avval xodimning joriy chiptasini yakunlang')
                        c.execute('UPDATE users SET role=?,window=?,enabled=? WHERE name=?',(body['role'],int(body['window']),body.get('enabled',True),body['name']))
                        if body.get('password'):c.execute('UPDATE users SET salt=?,hash=? WHERE name=?',(salt,password(body['password'],salt),body['name']))
                        c.execute('DELETE FROM sessions WHERE user=?',(body['name'],))
                        c.execute('DELETE FROM permissions WHERE user=?',(body['name'],))
                    else:
                        c.execute('INSERT INTO users(name,salt,hash,role,window,enabled) VALUES (?,?,?,?,?,?)',(body['name'],salt,password(body['password'],salt),body['role'],int(body['window']),body.get('enabled',True)))
                    c.executemany('INSERT INTO permissions(user,service) VALUES (?,?)',[(body['name'],s) for s in set(services)])
                return self.send(200,{'ok':True})
            return self.send(404,{'error':'Not found'})
        except (ValueError,KeyError,TypeError,OverflowError,sqlite3.IntegrityError) as error:
            message='Bunday yozuv mavjud yoki kiritilgan bog‘lanish noto‘g‘ri' if isinstance(error,sqlite3.IntegrityError) else 'So‘rov JSON shaklida noto‘g‘ri' if isinstance(error,json.JSONDecodeError) else str(error)
            self.send(400,{'error':alphabet.text(message)})

    def binary(self,payload,mime,filename=None):
        self.send_response(200)
        self.send_header('Content-Type',mime)
        if filename:self.send_header('Content-Disposition','attachment; filename="'+filename+'"')
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'self'")
        self.end_headers()
        self.wfile.write(payload)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--init',action='store_true')
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8080)
    parser.add_argument('--backup',action='store_true')
    parser.add_argument('--configure-printer',metavar='WINDOWS_NAME')
    parser.add_argument('--reset-admin',action='store_true')
    args = parser.parse_args()
    if args.reset_admin:
        import getpass
        value = getpass.getpass('Administrator uchun yangi parol (kamida 12 belgi): ')
        if len(value) < 12:
            raise ValueError('Parol kamida 12 belgi bo‘lsin')
        salt = secrets.token_hex(16)
        with connect() as c:
            c.execute("UPDATE users SET salt=?,hash=? WHERE name='admin'", (salt,password(value,salt)))
            c.execute("DELETE FROM sessions WHERE user='admin'")
        return
    if args.init:
        import getpass
        initialize(getpass.getpass('Administrator uchun yangi parol (kamida 12 belgi): '))
        return
    initialize()
    if args.configure_printer:
        printer_adapter.configure_printer(connect,args.configure_printer)
        print('Dialogsiz chop etish sozlandi: '+args.configure_printer)
        return
    if args.backup:
        destination = DATA/'backups'
        destination.mkdir(exist_ok=True)
        with connect() as source, sqlite3.connect(destination/(dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'.db')) as target:
            source.backup(target)
        return
    run_server(args.host,args.port)


def run_server(host,port,stop=None):
    import runtime
    with runtime.InstanceLock(DATA):
        if os.name=='nt':
            try:
                if printer_adapter.configure_printer(connect,automatic=True):
                    print('Dialogsiz printer: '+printer_adapter.KIOSK_PRINTER,flush=True)
            except (OSError,ValueError,subprocess.SubprocessError) as exc:
                logging.getLogger('navbat').warning('Printer avtomatik sozlanmadi: %s',exc)
        server=ThreadingHTTPServer((host,port),Handler)
        server.timeout=0.5
        log=RotatingFileHandler(DATA/'server.log',maxBytes=1024*1024,backupCount=3,encoding='utf-8')
        logger=logging.getLogger('navbat');logger.addHandler(log);logger.setLevel(logging.INFO)
        worker=printer_adapter.Worker(connect,DATA,ROOT);worker.start()
        runtime.start_backups(connect,DATA)
        if stop is None:print(f'Navbat serveri: {host}:{port}',flush=True)
        else:logger.info('Navbat xizmati ishga tushdi')
        try:
            if stop is None:server.serve_forever()
            else:
                while not stop.is_set():server.handle_request()
        finally:
            worker.stop.set();server.server_close();logger.removeHandler(log);log.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except (ValueError,RuntimeError,OSError) as error:
        import sys
        print(alphabet.text('Ishga tushirish xatosi: ')+alphabet.text(str(error)),file=sys.stderr)
        raise SystemExit(1)
