import concurrent.futures
from pathlib import Path
import tempfile
import unittest
import app
import management

class Operators(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.old_data=app.DATA;app.DATA=Path(self.temp.name)
        app.initialize('test-operator-admin-123')
        self.operators=[{'name':'operator'+str(n),'role':'staff','window':n} for n in range(1,6)]
        with app.connect() as c:
            for u in self.operators:
                c.execute('INSERT INTO users(name,salt,hash,role,window) VALUES (?,?,?,?,?)',(u['name'],'unused','unused','staff',u['window']))
                c.execute('INSERT INTO permissions VALUES (?,?)',(u['name'],1))
    def tearDown(self):app.DATA=self.old_data;self.temp.cleanup()
    def test_every_operator_has_all_departments(self):
        with app.connect() as c:
            for u in self.operators:self.assertEqual(set(management.allowed(c,u)),{1,2,3,4,5})
    def test_five_operators_claim_different_tickets_across_all_departments(self):
        tickets=[app.issue(n,f'five-operator-request-{n:016}') for n in range(1,6)]
        with concurrent.futures.ThreadPoolExecutor(5) as pool:claims=list(pool.map(lambda u:app.action(u,'next'),self.operators))
        self.assertTrue(all(claims));self.assertEqual({r['id'] for r in claims},{t['id'] for t in tickets})
        self.assertEqual({r['window'] for r in claims},{1,2,3,4,5})
    def test_specific_ticket_and_department_selection(self):
        first=app.issue(1,'specific-first-request-123');second=app.issue(4,'specific-second-request-123')
        self.assertEqual(app.action(self.operators[0],'next',ticket=second['id'])['id'],second['id'])
        with self.assertRaises(ValueError):app.action(self.operators[1],'next',ticket=second['id'])
        self.assertIsNone(app.action(self.operators[1],'next',service=4))
        self.assertEqual(app.action(self.operators[1],'next',service=1)['id'],first['id'])
    def test_single_ticket_cannot_be_claimed_twice(self):
        ticket=app.issue(5,'single-shared-ticket-123')
        with concurrent.futures.ThreadPoolExecutor(5) as pool:claims=list(pool.map(lambda u:app.action(u,'next'),self.operators))
        claimed=[r for r in claims if r]
        self.assertEqual(len(claimed),1);self.assertEqual(claimed[0]['id'],ticket['id'])
