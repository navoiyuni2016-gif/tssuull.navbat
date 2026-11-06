import database
import base64
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import http.cookiejar
import wave
import app
import alphabet
import audio_store
import management
import printer_adapter
import runtime


def wav_bytes():
    stream=io.BytesIO()
    with wave.open(stream,'wb') as output:
        output.setnchannels(1);output.setsampwidth(2);output.setframerate(8000);output.writeframes(b'\0\0'*800)
    return stream.getvalue()


class Features(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.old_data=app.DATA;app.DATA=Path(self.temp.name)
        app.initialize('test-password-12345')
    def tearDown(self):app.DATA=self.old_data;self.temp.cleanup()
    def test_alphabet(self):
        self.assertEqual(alphabet.text('Shahar, chipta, G‘oya, O‘zbekiston'), 'Şahar, çipta, Ğoya, Özbekiston')
        self.assertEqual(alphabet.text('SHAHAR CH O\'ZBEK G\'OYA'),'ŞAHAR Ç ÖZBEK ĞOYA')
    def test_audio_validation_and_persistence(self):
        with app.connect() as c:
            result=audio_store.save(c,app.DATA/'audio',{'slot':'digit_0','name':'nol.wav','content':base64.b64encode(wav_bytes()).decode(),'rights_confirmed':True})
            self.assertTrue(result['url'].startswith('/audio/'))
            self.assertEqual((app.DATA/'audio'/result['url'].split('/')[-1]).read_bytes(),wav_bytes())
            for slot,data,rights in [('../../bad',wav_bytes(),True),('digit_1',b'<script>x</script>',True),('digit_1',wav_bytes(),False),('digit_1',wav_bytes()[:-5],True)]:
                with self.assertRaises(ValueError):audio_store.save(c,app.DATA/'audio',{'slot':slot,'name':'bad.wav','content':base64.b64encode(data).decode(),'rights_confirmed':rights})
        app.initialize()
        with app.connect() as c:self.assertIn('digit_0',audio_store.manifest(c))
    def test_all_department_access_survives_restart_and_transfer(self):
        with app.connect() as c:
            c.execute("INSERT INTO users(name,salt,hash,role,window) VALUES ('worker','salt','unused','staff',2)")
            c.execute("INSERT INTO permissions VALUES ('worker',2)")
        a=app.issue(1,'request-first-service-123');b=app.issue(2,'request-second-service-123')
        app.initialize()
        worker={'name':'worker','role':'staff','window':2}
        self.assertEqual(app.action(worker,'next',service=2)['id'],b['id'])
        app.action(worker,'transfer',b['id'],1)
        with app.connect() as c:self.assertEqual(c.execute('SELECT service FROM calls WHERE ticket=?',(b['id'],)).fetchone()[0],2)
        self.assertIsNone(app.action(worker,'next',service=2))
        admin={'name':'admin','role':'admin','window':1}
        self.assertEqual(app.action(admin,'next')['id'],a['id'])
    def test_report_known_durations(self):
        t=app.issue(1,'request-report-123456')
        with app.connect() as c:
            c.execute("UPDATE tickets SET created='2026-11-05T09:00:00+05:00',day='2026-11-05',called='2026-11-05T09:02:00+05:00',started='2026-11-05T09:03:00+05:00',finished='2026-11-05T09:08:00+05:00',status='done',user='admin' WHERE id=?",(t['id'],))
            r=management.report(c,'2026-11-05','2026-11-05')
        self.assertEqual((r['issued'],r['done'],r['average_wait_seconds'],r['average_service_seconds']),(1,1,120,300))
    def test_backup_and_printer_failure_do_not_issue_new_ticket(self):
        with app.connect() as c:management.save_settings(c,{'printer_mode':'windows','printer_name':'missing-test-printer'})
        t=app.issue(1,'request-printer-123456')
        worker=printer_adapter.Worker(app.connect,app.DATA,app.ROOT);worker.once()
        self.assertEqual(app.issue(1,'request-printer-123456')['id'],t['id'])
        with app.connect() as c:
            self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],1)
            self.assertIn(c.execute('SELECT status FROM print_jobs').fetchone()[0],('failed','uncertain'))
        path=runtime.backup(app.connect,app.DATA)
        with database.connect(path) as c:self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],1)
    def test_work_hours_and_number_rule(self):
        with app.connect() as c:management.save_settings(c,{'weekdays':[(app.dt.datetime.now(app.TZ).weekday()+1)%7]})
        with self.assertRaises(ValueError):app.issue(1,'request-closed-123456')
        with app.connect() as c:management.save_settings(c,{'weekdays':list(range(7)),'prefix':'B','daily_reset':False})
        with app.connect() as c:c.execute("UPDATE services SET prefix='Z' WHERE id=1")
        self.assertEqual(app.issue(1,'request-prefix-123456')['label'],'Z001')

    def test_english_migration_and_ticket_print_language(self):
        old=app.issue(1,'language-before-migration-123')
        with app.connect() as c:
            c.execute('ALTER TABLE services DROP COLUMN name_en')
            c.execute('ALTER TABLE tickets DROP COLUMN lang')
            c.execute('PRAGMA user_version=2')
        app.initialize()
        with app.connect() as c:
            self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],3)
            self.assertEqual(c.execute('SELECT lang FROM tickets WHERE id=?',(old['id'],)).fetchone()[0],'uz')
            self.assertEqual(c.execute('SELECT name_en FROM services WHERE id=2').fetchone()[0],'Research and Innovation Services Sector')
        ticket=app.issue(2,'language-english-request-123','en')
        self.assertEqual(app.issue(2,'language-english-request-123','uz')['id'],ticket['id'])
        self.assertEqual(ticket['lang'],'en')
        with app.connect() as c:
            row=c.execute('SELECT tickets.*,services.name AS service_name,services.name_en AS service_name_en,services.name_ru AS service_name_ru FROM tickets JOIN services ON services.id=tickets.service WHERE tickets.id=?',(ticket['id'],)).fetchone()
            output=printer_adapter.preview(row,printer_adapter.service_name(row),'University')
            self.assertIn('Research and Innovation Services Sector',output)
            self.assertIn('People ahead',output)
            self.assertNotIn('Researç',output)
        with self.assertRaises(ValueError):app.issue(1,'language-cyrillic-request-123','cy')


class HTTP(unittest.TestCase):
    setUp=Features.setUp
    tearDown=Features.tearDown
    # Keep transport scenarios separate from domain cases above.
    def test_http_upload_permissions_and_flow(self):
        server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        base=f'http://127.0.0.1:{server.server_port}'
        client=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def request(path,body=None,origin=None):
            headers={'Content-Type':'application/json'}
            if origin:headers['Origin']=origin
            req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
            with client.open(req) as response:return json.load(response)
        try:
            upload={'slot':'digit_0','name':'zero.wav','content':base64.b64encode(wav_bytes()).decode(),'rights_confirmed':True}
            with self.assertRaises(urllib.error.HTTPError) as error:request('/api/audio/upload',upload)
            self.assertEqual(error.exception.code,403)
            with self.assertRaises(urllib.error.HTTPError):request('/api/tickets',{'service':1,'request':'cross-origin-key-12345'},'http://evil.example')
            with client.open(base+'/logo') as response:
                self.assertEqual(response.headers['Content-Type'],'image/png')
                self.assertEqual(response.read(),(app.ROOT/'web'/'assets'/'university-logo.png').read_bytes())
            self.assertTrue(request('/api/state')['custom_logo'])
            with self.assertRaises(urllib.error.HTTPError) as denied:request('/api/reports/export?format=pdf')
            self.assertEqual(denied.exception.code,403)
            request('/api/login',{'name':'admin','password':'test-password-12345'})
            png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/NmsAAAAASUVORK5CYII=')
            request('/api/logo',{'content':base64.b64encode(png).decode()})
            self.assertTrue(request('/api/state')['custom_logo'])
            with client.open(base+'/logo') as response:self.assertEqual(response.read(),png)
            recording=request('/api/audio/upload',upload)
            with client.open(base+recording['url']) as response:self.assertEqual(response.read(),wav_bytes())
            request('/api/users',{'name':'worker','password':'worker-password-123','role':'staff','window':2,'services':[1]})
            ticket=request('/api/tickets',{'service':1,'request':'http-request-123456'})
            self.assertEqual(request('/api/action',{'action':'next'})['id'],ticket['id'])
            request('/api/action',{'action':'recall','ticket':ticket['id']})
            self.assertEqual(len(request('/api/calls?after=0')['calls']),2)
            self.assertEqual(len(request('/api/calls?after=1')['calls']),1)
            request('/api/action',{'action':'start','ticket':ticket['id']})
            self.assertEqual(request('/api/action',{'action':'finish','ticket':ticket['id']})['status'],'done')
            self.assertEqual(request('/api/reports')['done'],1)
            for fmt in ('xlsx','docx','pdf'):
                with client.open(base+'/api/reports/export?format='+fmt) as response:
                    self.assertIn('attachment',response.headers['Content-Disposition']);payload=response.read();self.assertTrue(payload.startswith(b'%PDF') if fmt=='pdf' else payload.startswith(b'PK'))
            request('/api/logout',{})
            request('/api/login',{'name':'worker','password':'worker-password-123'})
            for endpoint,body in [('/api/audio/upload',upload),('/api/settings',{'prefix':'B'})]:
                with self.assertRaises(urllib.error.HTTPError) as e:request(endpoint,body)
                self.assertEqual(e.exception.code,403)
        finally:server.shutdown();server.server_close()
