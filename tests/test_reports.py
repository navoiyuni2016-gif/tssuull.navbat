import io
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
import app
import report_exports

class Reports(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.old=app.DATA;app.DATA=Path(self.temp.name);app.initialize('report-admin-password-123')
        ticket=app.issue(1,'report-fixture-request-123')
        with app.connect() as c:
            c.execute("UPDATE tickets SET day='2026-11-05',created='2026-11-05T09:00:00+05:00',called='2026-11-05T09:02:00+05:00',started='2026-11-05T09:03:00+05:00',finished='2026-11-05T09:08:00+05:00',status='done',user='admin' WHERE id=?",(ticket['id'],))
            self.data=report_exports.snapshot(c,'2026-11-05','2026-11-05')
    def tearDown(self):app.DATA=self.old;self.temp.cleanup()
    def office(self,kind):
        raw,mime,name=report_exports.render(self.data,kind);self.assertTrue(name.endswith('.'+kind))
        archive=zipfile.ZipFile(io.BytesIO(raw));self.assertIsNone(archive.testzip())
        for name in archive.namelist():
            if name.endswith(('.xml','.rels')):ET.fromstring(archive.read(name))
        return archive
    def test_xlsx_preserves_numeric_metrics_and_escapes_formula_names(self):
        self.data['groups'][0][1][0][0]='=HYPERLINK("https://example.invalid")'
        archive=self.office('xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        root=ET.fromstring(archive.read('xl/worksheets/sheet1.xml'));cells={c.attrib['r']:c for c in root.findall('.//s:c',ns)}
        self.assertEqual(cells['E7'].find('s:v',ns).text,'1');self.assertEqual(cells['E11'].find('s:v',ns).text,'2.0')
        group=ET.fromstring(archive.read('xl/worksheets/sheet2.xml'));cell=next(c for c in group.findall('.//s:c',ns) if c.attrib['r']=='A8');self.assertEqual(cell.attrib['t'],'inlineStr');self.assertIsNone(cell.find('s:f',ns));self.assertIn('xl/media/logo.png',archive.namelist())
    def test_docx_has_three_tables_full_names_and_logo(self):
        archive=self.office('docx');root=ET.fromstring(archive.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        self.assertEqual(len(root.findall('.//w:tbl',ns)),3);text=' '.join(t.text or '' for t in root.findall('.//w:t',ns));self.assertIn('2.0',text);self.assertIn('Operatorlar kesimida',text);self.assertIn('word/media/logo.png',archive.namelist())
    def test_minutes_served_totals_and_zero_activity_rows(self):
        import management
        with app.connect() as c:
            c.execute("INSERT INTO users(name,salt,hash,role,window) SELECT 'idle-worker',salt,hash,'staff',2 FROM users WHERE name='admin'")
            r=management.report(c,'2026-11-05','2026-11-05')
        self.assertEqual((r['average_wait_minutes'],r['average_service_minutes'],r['served']),(2,5,1))
        self.assertEqual(len(r['services']),5)
        self.assertEqual(r['services']['1']['served'],1)
        self.assertEqual(r['employees']['admin']['served'],1)
        self.assertEqual(r['employees']['idle-worker']['served'],0)
        self.assertIsNone(r['employees']['idle-worker']['average_wait_minutes'])
        self.assertEqual(sum(b['served'] for b in r['services'].values()),r['served'])
        self.assertEqual(sum(b['served'] for b in r['employees'].values()),r['served'])
    def test_export_tables_have_black_full_grid_without_colored_cells(self):
        archive=self.office('xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        styles=ET.fromstring(archive.read('xl/styles.xml'))
        border=styles.find('s:borders',ns)[1]
        for edge in ['left','right','top','bottom']:
            self.assertEqual(border.find('s:'+edge,ns).attrib['style'],'thin')
            self.assertEqual(border.find('s:'+edge+'/s:color',ns).attrib['rgb'],'FF000000')
        for color in styles.findall('.//s:fgColor',ns):self.assertEqual(color.attrib['rgb'],'FFFFFFFF')
        archive=self.office('docx');ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        root=ET.fromstring(archive.read('word/document.xml'))
        for table in root.findall('.//w:tbl',ns):
            for edge in ['top','left','bottom','right','insideH','insideV']:
                self.assertEqual(table.find('w:tblPr/w:tblBorders/w:'+edge,ns).attrib['{'+ns['w']+'}color'],'000000')
        for shading in root.findall('.//w:shd',ns):self.assertEqual(shading.attrib['{'+ns['w']+'}fill'],'FFFFFF')
    def test_pdf_has_valid_xref_unicode_font_and_metrics(self):
        raw,mime,name=report_exports.render(self.data,'pdf');self.assertEqual(mime,'application/pdf');self.assertTrue(raw.startswith(b'%PDF-1.4'));self.assertIn(b'/ToUnicode',raw);self.assertIn(b'/FontFile2',raw);self.assertIn(b'/Subtype /Image',raw)
        xref=int(raw.rsplit(b'startxref\n',1)[1].splitlines()[0]);self.assertEqual(raw[xref:xref+4],b'xref')
        rows=raw[xref:].splitlines();count=int(rows[1].split()[1]);offsets=[int(row.split()[0]) for row in rows[3:3+count-1]]
        for n,offset in enumerate(offsets,1):self.assertTrue(raw[offset:].startswith(f'{n} 0 obj'.encode()))
    def test_empty_report_and_invalid_format(self):
        with app.connect() as c:data=report_exports.snapshot(c,'2020-01-01','2020-01-02')
        self.assertEqual(data['summary'][0][1],0)
        for kind in ['xlsx','docx','pdf']:self.assertGreater(len(report_exports.render(data,kind)[0]),1000)
        with self.assertRaises(ValueError):report_exports.render(data,'exe')
