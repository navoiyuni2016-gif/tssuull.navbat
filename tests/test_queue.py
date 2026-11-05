import concurrent.futures
import importlib
import os
from pathlib import Path
import tempfile
import unittest
import app

class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        app.DATA=Path(self.temp.name)
        app.initialize('test-password-12345')
        self.user={'name':'admin','window':1,'role':'admin'}
    def tearDown(self): self.temp.cleanup()
    def test_duplicate_parallel_issue(self):
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            rows=list(pool.map(lambda _:app.issue(1,'same-request-key-123'),range(16)))
        self.assertEqual(len({r['id'] for r in rows}),1)
    def test_numbering_and_claims(self):
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            rows=list(pool.map(lambda n:app.issue(1,f'request-key-{n:016}'),range(20)))
        self.assertEqual(len({r['number'] for r in rows}),20)
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            claims=list(pool.map(lambda n:app.action({'name':'admin','window':n,'role':'admin'},'next'),[1,2]))
        self.assertNotEqual(claims[0]['id'],claims[1]['id'])
    def test_flow_and_persistence(self):
        t=app.issue(1,'request-key-123456')
        called=app.action(self.user,'next')
        self.assertEqual(called['id'],t['id'])
        with self.assertRaises(ValueError): app.action(self.user,'finish',t['id'])
        app.action(self.user,'start',t['id'])
        app.action(self.user,'finish',t['id'])
        app.initialize()
        self.assertEqual(app.issue(1,'request-key-123456')['status'],'done')
    def test_reused_key_different_service(self):
        app.issue(1,'request-key-123456')
        with self.assertRaises(ValueError): app.issue(2,'request-key-123456')

if __name__=='__main__': unittest.main()
