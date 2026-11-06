import database
import json
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import http.cookiejar
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
import app,management,printer_adapter

class ReliablePrinting(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.previous=app.DATA;app.DATA=Path(self.folder.name);app.initialize('reliable-print-password-123')
        printer_adapter.apply_kiosk_preset(app.connect)
    def tearDown(self):app.DATA=self.previous;self.folder.cleanup()
    def test_validators_and_manual_settings_survive_restart(self):
        for body in [{'printer_mode':'bad'},{'printer_name':None},{'printer_name':' '},{'paper_width_mm':57},{'paper_width_mm':101},{'paper_width_mm':'80'},{'paper_width_mm':True}]:
            with app.connect() as c:
                with self.assertRaises(ValueError):management.save_settings(c,body)
        with app.connect() as c:management.save_settings(c,{'printer_name':'Other printer','paper_width_mm':58})
        app.initialize();printer_adapter.apply_kiosk_preset(app.connect)
        with app.connect() as c:self.assertEqual((management.settings(c)['printer_name'],management.settings(c)['paper_width_mm']),('Other printer',58))
    def test_repairs_bad_legacy_values_without_deleting_ticket(self):
        ticket=app.issue(1,'legacy-printer-config-request')
        with app.connect() as c:
            c.execute("UPDATE settings SET value='null' WHERE key='printer_name'");c.execute("UPDATE settings SET value='1' WHERE key='paper_width_mm'");c.execute("UPDATE settings SET value='\"broken\"' WHERE key='printer_mode'")
        app.initialize()
        with app.connect() as c:
            config=management.settings(c);self.assertEqual((config['printer_mode'],config['printer_name'],config['paper_width_mm']),('windows','KPOS_80 Printer(1)',80))
            self.assertEqual(c.execute('SELECT label FROM tickets WHERE id=?',(ticket['id'],)).fetchone()[0],ticket['label'])
    def test_worker_success_failure_uncertain_and_recovery(self):
        ticket=app.issue(1,'worker-print-state-request-123');payloads=[]
        def sender(payload):
            with app.connect() as c:self.assertEqual(c.execute('SELECT status FROM print_jobs').fetchone()[0],'printing')
            payloads.append(payload)
        worker=printer_adapter.Worker(app.connect,app.DATA,app.ROOT,sender=sender);worker.once();worker.once()
        self.assertEqual(len(payloads),1);self.assertEqual(payloads[0]['width'],80);self.assertEqual(payloads[0]['label'],ticket['label'])
        for error,expected in [(ValueError('USB offline'),'failed'),(printer_adapter.PrintUncertain('unknown paper'),'uncertain')]:
            with app.connect() as c:c.execute("UPDATE print_jobs SET status='pending'")
            def fail(payload):raise error
            printer_adapter.Worker(app.connect,app.DATA,app.ROOT,sender=fail).once()
            with app.connect() as c:self.assertEqual(c.execute('SELECT status FROM print_jobs').fetchone()[0],expected)
        with app.connect() as c:c.execute("UPDATE print_jobs SET status='printing'")
        worker.start();worker.close()
        with app.connect() as c:self.assertEqual(c.execute('SELECT status FROM print_jobs').fetchone()[0],'uncertain')
        self.assertEqual(len(payloads),1)
    def test_http_reprint_dedup_and_separate_diagnostic_queue(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),app.Handler);thread=threading.Thread(target=server.serve_forever);thread.start()
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));base='http://127.0.0.1:'+str(server.server_port)
        def request(path,body=None):
            req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
            with opener.open(req) as response:return json.load(response)
        try:
            with self.assertRaises(urllib.error.HTTPError):request('/api/printer')
            with self.assertRaises(urllib.error.HTTPError):request('/api/printer/test',{'request':'diagnostic-request-123'})
            request('/api/login',{'name':'admin','password':'reliable-print-password-123'})
            for _ in range(2):request('/api/printer/test',{'request':'diagnostic-request-123'})
            payloads=[];worker=printer_adapter.Worker(app.connect,app.DATA,app.ROOT,sender=payloads.append);worker.once()
            with app.connect() as c:
                self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],0);self.assertEqual(c.execute('SELECT count(*) FROM printer_tests').fetchone()[0],1)
            self.assertEqual(payloads[0]['label'],'TEST')
            ticket=app.issue(1,'reprint-dedup-ticket-request');worker.once()
            first=request('/api/print/status',{'request':ticket['request']})['job']
            body={'request':ticket['request'],'previous_job':first['id'],'attempt':'retry-once-attempt-123'}
            second=request('/api/print',body)['job'];worker.once()
            self.assertEqual(request('/api/print',body)['job']['id'],second['id'])
            body['attempt']='different-stale-attempt-123'
            self.assertEqual(request('/api/print',body)['job']['id'],second['id'])
            with app.connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM print_jobs').fetchone()[0],2)
        finally:server.shutdown();server.server_close();thread.join()
