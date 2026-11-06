"""Run against the real packaged executable on the Windows build runner."""
import json
import database
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import time
import unittest
import urllib.request

@unittest.skipUnless(os.name=='nt' and os.environ.get('NAVBAT_EXE'),'Windows packaged build only')
class FrozenWindows(unittest.TestCase):
    def test_frozen_tk_resources_reports_and_server(self):
        exe=os.environ['NAVBAT_EXE']
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);result=root/'self-test.json'
            process=subprocess.run([exe,'--self-test',str(result)],timeout=120)
            self.assertEqual(process.returncode,0)
            body=json.loads(result.read_text(encoding='utf-8'));self.assertTrue(body.get('ok'),body);self.assertTrue(body['frozen'])
            import app
            previous=app.DATA;app.DATA=root/'data'
            try:app.initialize('frozen-server-test-password-123')
            finally:app.DATA=previous
            environment=dict(os.environ,NAVBAT_DATA=str(root/'data'))
            diagnostic=root/'printer-diagnostics.json'
            diagnosed=subprocess.run([exe,'--diagnostics',str(diagnostic)],env=environment,timeout=60)
            self.assertEqual(diagnosed.returncode,0)
            report=json.loads(diagnostic.read_text(encoding='utf-8'))
            self.assertFalse(report['physical_test_verified']);self.assertIsInstance(report['printers'],list)
            self.assertTrue(report.get('account'),report);self.assertFalse(report['tests'])
            with database.connect(root/'data'/'queue.db') as c:self.assertEqual(c.execute('SELECT count(*) FROM print_jobs').fetchone()[0],0)
            log=(root/'server.log').open('wb')
            server=subprocess.Popen([exe,'--server'],env=environment,stdout=log,stderr=log)
            try:
                opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));ready=False
                for _ in range(100):
                    try:
                        with opener.open('http://127.0.0.1:8080/api/health',timeout=1) as response:
                            self.assertEqual(json.load(response)['app'],'toshdotau-navbat');ready=True;break
                    except OSError:
                        if server.poll() is not None:break
                        time.sleep(.2)
                self.assertTrue(ready,'Frozen server did not start')
                with database.connect(root/'data'/'queue.db') as c:
                    config={key:json.loads(value) for key,value in c.execute('SELECT key,value FROM settings')}
                    self.assertEqual((config['printer_mode'],config['printer_name'],config['paper_width_mm']),('windows','KPOS_80 Printer(1)',80))
                with opener.open('http://127.0.0.1:8080/',timeout=5) as response:self.assertIn(b'/app.js',response.read())
                payload=json.dumps({'service':1,'request':'frozen-http-ticket-request-123'}).encode()
                request=urllib.request.Request('http://127.0.0.1:8080/api/tickets',data=payload,headers={'Content-Type':'application/json'})
                with opener.open(request,timeout=5) as response:self.assertEqual(json.load(response)['label'],'A001')
            finally:
                if server.poll() is None:server.terminate()
                server.wait(timeout=15);log.close()

    def test_actual_native_webview_window(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'native.json'
            try:completed=subprocess.run([os.environ['NAVBAT_EXE'],'--native-self-test',str(path)],timeout=120)
            except subprocess.TimeoutExpired:self.fail('Native window timed out')
            body=json.loads(path.read_text()) if path.exists() else {'error':'native result missing'}
            self.assertEqual(completed.returncode,0,body);self.assertTrue(body.get('ok'),body)
            self.assertEqual(body['renderer'],'edgechromium');self.assertTrue(body['native_window']);self.assertTrue(body['admin_login'])
