import concurrent.futures
import http.cookiejar
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import app

class OperatorHTTP(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.old=app.DATA;app.DATA=Path(self.temp.name);app.initialize('http-operator-admin-123')
        self.server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler);threading.Thread(target=self.server.serve_forever,daemon=True).start();self.base=f'http://127.0.0.1:{self.server.server_port}'
        self.admin=self.client();self.request(self.admin,'login',{'name':'admin','password':'http-operator-admin-123'});self.operators=[]
        for n in range(1,6):
            name='operator'+str(n);self.request(self.admin,'users',{'name':name,'password':'operator-test-pass-123','role':'staff','window':n,'services':[1]})
            client=self.client();self.request(client,'login',{'name':name,'password':'operator-test-pass-123'});self.operators.append(client)
    def tearDown(self):self.server.shutdown();self.server.server_close();app.DATA=self.old;self.temp.cleanup()
    def client(self):return urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def request(self,client,path,body=None):
        req=urllib.request.Request(self.base+'/api/'+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
        with client.open(req) as response:return json.load(response)
    def test_all_five_see_and_claim_all_departments_and_see_other_windows(self):
        tickets=[self.request(self.admin,'tickets',{'service':n,'request':f'http-all-operator-{n:016}'}) for n in range(1,6)]
        for client in self.operators:self.assertEqual({t['service'] for t in self.request(client,'work')['tickets']},{1,2,3,4,5})
        with concurrent.futures.ThreadPoolExecutor(5) as pool:claims=list(pool.map(lambda client:self.request(client,'action',{'action':'next'}),self.operators))
        self.assertEqual({t['id'] for t in claims},{t['id'] for t in tickets})
        for n,client in enumerate(self.operators,1):
            work=self.request(client,'work');self.assertEqual(len(work['active_windows']),4);self.assertEqual(len(work['tickets']),1);self.assertEqual(work['tickets'][0]['window'],n)
            with self.assertRaises(urllib.error.HTTPError) as error:self.request(client,'settings',{'prefix':'B'})
            self.assertEqual(error.exception.code,403)
    def test_specific_ticket_is_claimed_once_over_http(self):
        ticket=self.request(self.admin,'tickets',{'service':5,'request':'http-single-specific-123'})
        def claim(client):
            try:return self.request(client,'action',{'action':'next','ticket':ticket['id']})['id']
            except urllib.error.HTTPError as error:self.assertEqual(error.code,400);return None
        with concurrent.futures.ThreadPoolExecutor(5) as pool:claims=list(pool.map(claim,self.operators))
        self.assertEqual(claims.count(ticket['id']),1)
