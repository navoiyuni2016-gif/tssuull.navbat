import tempfile
import unittest
from pathlib import Path
import app,display_adapter

class Displays(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.old=app.DATA;app.DATA=Path(self.temp.name);app.initialize('display-test-password-123')
        self.user={'name':'admin','role':'admin','window':5}
        with app.connect() as c:
            for n in range(1,6):display_adapter.save(c,dict(window=n,device_address=str(n),transport='mock',endpoint='',enabled=True))
    def tearDown(self):app.DATA=self.old;self.temp.cleanup()
    def test_call_recall_and_clear_only_target_window(self):
        ticket=app.issue(1,'display-five-window-request')
        app.action(self.user,'next');worker=display_adapter.Worker(app.connect);self.assertTrue(worker.once())
        with app.connect() as c:
            devices=display_adapter.state(c)['devices'];self.assertEqual([d['last_value'] for d in devices],[None,None,None,None,ticket['label']])
            self.assertFalse(any(d['physical_verified'] for d in devices))
        app.action(self.user,'recall',ticket['id']);self.assertTrue(worker.once())
        app.action(self.user,'start',ticket['id']);app.action(self.user,'finish',ticket['id']);self.assertTrue(worker.once())
        with app.connect() as c:
            self.assertEqual(c.execute('SELECT last_value FROM display_devices WHERE window=5').fetchone()[0],'')
            self.assertEqual(c.execute('SELECT count(*) FROM calls').fetchone()[0],2)
            self.assertEqual([r[0] for r in c.execute('SELECT status FROM display_jobs')],['simulated']*3)
    def test_unverified_transport_is_blocked_without_affecting_queue(self):
        with app.connect() as c:display_adapter.save(c,dict(window=5,device_address='5',transport='serial',endpoint='COM8',enabled=True))
        ticket=app.issue(2,'display-unverified-request');self.assertEqual(app.action(self.user,'next')['id'],ticket['id'])
        with app.connect() as c:
            self.assertEqual(c.execute('SELECT status FROM display_jobs').fetchone()[0],'blocked')
            device=c.execute('SELECT id FROM display_devices WHERE window=5').fetchone()[0]
            with self.assertRaises(ValueError):display_adapter.command(c,dict(device=device,operation='show',value='B025'))
        self.assertFalse(display_adapter.Worker(app.connect).once())
    def test_missing_display_table_does_not_undo_call(self):
        ticket=app.issue(1,'display-error-isolation-request')
        with app.connect() as c:c.execute('DROP TABLE display_jobs')
        with self.assertLogs('navbat',level='ERROR'):app.action(self.user,'next')
        with app.connect() as c:
            self.assertEqual(c.execute('SELECT status FROM tickets WHERE id=?',(ticket['id'],)).fetchone()[0],'called')
            self.assertEqual(c.execute('SELECT count(*) FROM calls').fetchone()[0],1)
    def test_invalid_device_identifier_is_rejected(self):
        with app.connect() as c:
            for identifier in [None,True,0,{},[], '1']:
                with self.assertRaises(ValueError):display_adapter.command(c,dict(device=identifier,operation='show',value='A025'))
    def test_manual_test_has_no_ticket_and_settings_survive_restart(self):
        with app.connect() as c:
            device=c.execute('SELECT id FROM display_devices WHERE window=2').fetchone()[0]
            display_adapter.command(c,dict(device=device,operation='show',value='E123'))
        display_adapter.Worker(app.connect).once();app.initialize()
        with app.connect() as c:
            self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT last_value FROM display_devices WHERE window=2').fetchone()[0],'E123')
            self.assertEqual(c.execute('SELECT count(*) FROM display_devices').fetchone()[0],5)
