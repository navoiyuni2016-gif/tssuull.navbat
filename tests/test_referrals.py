import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile
import app,management,referrals,report_exports,display_adapter

class Referrals(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.old=app.DATA;app.DATA=Path(self.temp.name);app.initialize('referral-test-password-123')
        with app.connect() as c:
            for n in range(1,6):c.execute("INSERT INTO users(name,salt,hash,role,window) SELECT ?,salt,hash,'staff',? FROM users WHERE name='admin'",('worker'+str(n),n))
        self.staff={'name':'worker5','role':'staff','window':5};self.admin={'name':'admin','role':'admin','window':1}
    def tearDown(self):app.DATA=self.old;self.temp.cleanup()
    def called(self,n=1):
        ticket=app.issue(n,'referral-ticket-request-'+str(n));app.action(self.staff,'next',ticket['id']);return ticket
    def forward(self,ticket,comment='Talabaning hujjati topilmadi'):
        return app.action(self.staff,'refer_admin',ticket['id'],comment=comment)
    def close(self,identifier,status='resolved',comment='Hujjat tekshirilib muammo hal qilindi',user=None):
        with app.connect() as c:
            c.execute('BEGIN IMMEDIATE');return referrals.resolve(c,user or self.admin,identifier,status,comment,app.now())
    def test_required_comment_owner_and_repeat_request(self):
        ticket=self.called()
        for comment in ['', '   ',None,'x'*1001]:
            with self.assertRaises(ValueError):self.forward(ticket,comment)
        with self.assertRaises(ValueError):app.action({'name':'worker1','role':'staff','window':1},'refer_admin',ticket['id'],comment='Begona chipta')
        self.assertEqual(self.forward(ticket)['status'],'referred');self.forward(ticket)
        with app.connect() as c:
            self.assertEqual(c.execute('SELECT count(*) FROM referrals').fetchone()[0],1)
            self.assertEqual(c.execute('SELECT count(*) FROM print_jobs').fetchone()[0],1)
            self.assertEqual(c.execute("SELECT count(*) FROM events WHERE operation='refer_admin'").fetchone()[0],1)
        # Operator is free; referred ticket cannot be called by another operator.
        self.assertIsNone(app.action(self.staff,'next'))
        with self.assertRaises(ValueError):app.action(self.staff,'next',ticket['id'])
    def test_all_five_operators_can_forward(self):
        for n in range(1,6):
            self.staff={'name':'worker'+str(n),'role':'staff','window':n}
            self.forward(self.called(n))
        with app.connect() as c:
            rows=referrals.listing(c);self.assertEqual(len(rows),5)
            self.assertEqual({r['window'] for r in rows},set(range(1,6)))
    def test_admin_only_outcomes_and_counting(self):
        first=self.called(1);self.forward(first)
        second=self.called(2);self.forward(second)
        with app.connect() as c:cases=referrals.listing(c)
        first_case=next(r for r in cases if r['ticket']==first['id']);second_case=next(r for r in cases if r['ticket']==second['id'])
        with self.assertRaises(ValueError):self.close(first_case['id'],user=self.staff)
        with self.assertRaises(ValueError):self.close(first_case['id'],comment=' ')
        self.close(first_case['id']);self.close(first_case['id']) # Safe identical retry.
        self.close(second_case['id'],'unresolved','Tashqi tashkilot javobi olinmadi')
        with self.assertRaises(ValueError):self.close(first_case['id'],'unresolved','Oldingi natijani almashtirish')
        with app.connect() as c:
            report=management.report(c,first['day'],first['day'])
            self.assertEqual((report['referrals']['resolved'],report['referrals']['unresolved'],report['referrals']['pending']),(1,1,0))
            self.assertEqual(report['served'],1);self.assertEqual(report['employees']['admin']['served'],1)
            self.assertEqual(c.execute('SELECT count(*) FROM referral_history').fetchone()[0],4)
            self.assertEqual(c.execute('SELECT status FROM tickets WHERE id=?',(second['id'],)).fetchone()[0],'unresolved')
    def test_restart_preserves_problem_and_only_own_staff_history(self):
        ticket=self.called();self.forward(ticket,'Muammo: O‘qish hujjati & ariza <tekshiruv>')
        app.initialize()
        with app.connect() as c:
            self.assertEqual(referrals.listing(c,operator='worker1'),[])
            row=referrals.listing(c,operator='worker5')[0]
            self.assertEqual((row['label'],row['window'],row['status']),(ticket['label'],5,'pending'))
            self.assertIn('<tekshiruv>',row['comment'])
    def test_report_cohort_uses_referral_date_and_led_clears(self):
        with app.connect() as c:display_adapter.save(c,dict(window=5,device_address='5',transport='mock',endpoint='',enabled=True))
        ticket=self.called();worker=display_adapter.Worker(app.connect);worker.once()
        with patch('app.now',return_value='2020-02-03T12:00:00+05:00'):self.forward(ticket)
        worker.once()
        with app.connect() as c:
            report=management.report(c,'2020-02-03','2020-02-03')
            self.assertEqual(report['issued'],0);self.assertEqual(report['referrals']['pending'],1)
            self.assertEqual(c.execute('SELECT last_value FROM display_devices WHERE window=5').fetchone()[0],'')
    def test_case_details_exported_to_office_and_pdf(self):
        ticket=self.called();self.forward(ticket,'=HYPERLINK("bad") & tekshiruv')
        with app.connect() as c:case=referrals.listing(c)[0]
        self.close(case['id'],'unresolved','Yakuniy javob kutilmoqda')
        with app.connect() as c:data=report_exports.snapshot(c,ticket['day'],ticket['day'])
        self.assertEqual(data['issues'][0][0],ticket['label']);self.assertIn('Hal qilinmadi',data['issues'][0])
        for fmt in ('xlsx','docx'):
            archive=zipfile.ZipFile(io.BytesIO(report_exports.render(data,fmt)[0]));name='xl/worksheets/sheet4.xml' if fmt=='xlsx' else 'word/document.xml'
            xml=archive.read(name);ET.fromstring(xml)
            for text in ['Yakuniy javob kutilmoqda','worker5','Hal qilinmadi',ticket['label']]:self.assertIn(text,xml.decode())
            if fmt=='xlsx':self.assertNotIn(b'<f>',xml)
        self.assertTrue(report_exports.render(data,'pdf')[0].startswith(b'%PDF'))
