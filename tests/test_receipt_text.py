import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import app
import management
import printer_adapter

EN="Alisher Navo'i Tashkent State University of Uzbek Language and Literature"
RU='Ташкентский государственный университет узбекского языка и литературы имени Алишера Навои'

class ReceiptText(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.previous=app.DATA
        app.DATA=Path(self.temp.name);app.initialize('receipt-text-password-123')
        printer_adapter.apply_kiosk_preset(app.connect)
    def tearDown(self):
        app.DATA=self.previous;self.temp.cleanup()
    def test_actual_ticketfile_json_preserves_last_letter_and_uses_ticket_language(self):
        captured=[]
        def powershell(command,**kwargs):
            captured.append(json.loads(Path(command[-1]).read_text(encoding='utf-8')))
            return SimpleNamespace(returncode=0,stdout=b'{"ok":true}',stderr=b'')
        for lang in ('uz','ru','en'):
            app.issue(1,'receipt-text-'+lang+'-request',lang=lang)
            worker=printer_adapter.Worker(app.connect,app.DATA,app.ROOT)
            with patch.object(printer_adapter,'os',SimpleNamespace(name='nt')),patch.object(printer_adapter.subprocess,'run',side_effect=powershell):worker.once()
        with app.connect() as c:original=management.settings(c)['university']
        self.assertIn('özbek',original)
        self.assertEqual([v['university'] for v in captured],[original,RU,EN])
        self.assertEqual([v['lang'] for v in captured],['uz','ru','en'])
        self.assertTrue(all(v['printer']=='KPOS_80 Printer(1)' and v['width']==80 for v in captured))
    def test_translations_validate_and_migration_preserves_custom_name_and_printer(self):
        with app.connect() as c:
            management.save_settings(c,{'university':'Maxsus universitet nomi','university_ru':'Пользовательское название','university_en':'Custom University','printer_name':'Existing printer','paper_width_mm':58})
        app.initialize()
        with app.connect() as c:
            cfg=management.settings(c)
            self.assertEqual((cfg['university'],cfg['university_ru'],cfg['university_en']),('Maxsus universitet nomi','Пользовательское название','Custom University'))
            self.assertEqual((cfg['printer_name'],cfg['paper_width_mm']),('Existing printer',58))
            for invalid in (None,1,'', 'a'*301):
                with self.assertRaises(ValueError):management.save_settings(c,{'university_en':invalid})

if __name__=='__main__':unittest.main()
