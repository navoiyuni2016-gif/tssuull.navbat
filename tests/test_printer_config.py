import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import app
import management
import printer_adapter


class PrinterConfiguration(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.previous=app.DATA
        app.DATA=Path(self.folder.name);app.initialize('printer-test-password-123')
    def tearDown(self):
        app.DATA=self.previous;self.folder.cleanup()
    def test_detected_kpos_queues_new_ticket_without_replaying_preview(self):
        old=app.issue(1,'preview-before-configuration-123')
        with patch.object(printer_adapter,'installed_printers',return_value=['KPOS_80 Printer(1)']):
            self.assertTrue(printer_adapter.configure_printer(app.connect,automatic=True))
        new=app.issue(2,'automatic-after-configuration-123')
        with app.connect() as c:
            cfg=management.settings(c)
            self.assertEqual((cfg['printer_mode'],cfg['printer_name'],cfg['paper_width_mm']),('windows','KPOS_80 Printer(1)',80))
            jobs=dict(c.execute('SELECT ticket,status FROM print_jobs').fetchall())
            self.assertEqual(jobs[old['id']],'preview');self.assertEqual(jobs[new['id']],'pending')
    def test_missing_driver_does_not_change_settings(self):
        with patch.object(printer_adapter,'installed_printers',return_value=['Other printer']):
            self.assertFalse(printer_adapter.configure_printer(app.connect,automatic=True))
            with self.assertRaises(ValueError):printer_adapter.configure_printer(app.connect)
        with app.connect() as c:self.assertEqual(management.settings(c)['printer_mode'],'html')
    def test_existing_windows_printer_is_preserved(self):
        with app.connect() as c:management.save_settings(c,dict(printer_mode='windows',printer_name='Existing driver'))
        with patch.object(printer_adapter,'installed_printers') as lookup:
            self.assertFalse(printer_adapter.configure_printer(app.connect,automatic=True));lookup.assert_not_called()
        with app.connect() as c:self.assertEqual(management.settings(c)['printer_name'],'Existing driver')
