import copy
import tempfile
import unittest
from pathlib import Path
import app,display_adapter

class DisplayProfiles(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.old=app.DATA;app.DATA=Path(self.temp.name);app.initialize('display-profile-password-123')
  self.body={'window':5,'device_address':'134','transport':'serial','endpoint':'COM2','enabled':True,'profile':{'baud_rate':19200,'parity':'E','data_bits':8,'stop_bits':'1','segments':4,'timeout_ms':1500,'tcp_port':None,'model':'Model not verified','protocol_note':'Parametrlarni texnik hujjat bilan tekshiring'}}
 def tearDown(self):app.DATA=self.old;self.temp.cleanup()
 def test_manual_parameters_persist_and_do_not_unlock_hardware(self):
  with app.connect() as c:display_adapter.save(c,self.body)
  app.initialize()
  with app.connect() as c:
   state=display_adapter.state(c);device=state['devices'][0]
   self.assertEqual(device['profile'],self.body['profile']);self.assertEqual(device['status'],'blocked');self.assertFalse(state['protocol_verified'])
   with self.assertRaises(ValueError):display_adapter.command(c,dict(device=device['id'],operation='show',value='A025'))
   old={k:self.body[k] for k in ['window','device_address','transport','endpoint','enabled']};display_adapter.save(c,old)
   self.assertEqual(display_adapter.state(c)['devices'][0]['profile'],self.body['profile'])
 def test_unknown_parameters_are_not_guessed(self):
  body={k:v for k,v in self.body.items() if k!='profile'}
  with app.connect() as c:
   display_adapter.save(c,body);self.assertEqual(display_adapter.state(c)['devices'][0]['profile'],{})
 def test_invalid_profile_parameters_are_rejected(self):
  for key,value in [('baud_rate',True),('baud_rate',-1),('parity','BAD'),('data_bits',9),('stop_bits','3'),('segments',0),('timeout_ms',0),('tcp_port',70000),('model','x'*201),('protocol_verified',True)]:
   body=copy.deepcopy(self.body);body['profile'][key]=value
   with app.connect() as c:
    with self.assertRaises(ValueError,msg=key):display_adapter.save(c,body)
 def test_export_import_roundtrip_and_invalid_batch_rollback(self):
  with app.connect() as c:
   display_adapter.save(c,self.body);profile=display_adapter.export_profile(c)
   self.assertEqual(profile['version'],1);self.assertNotIn('jobs',profile)
   self.assertNotIn('physical_verified',profile['devices'][0])
   changed=copy.deepcopy(profile);changed['devices'][0]['endpoint']='COM7'
   c.execute('BEGIN IMMEDIATE') if not c.in_transaction else None
   display_adapter.import_profile(c,changed)
  with app.connect() as c:
   c.execute('BEGIN IMMEDIATE');display_adapter.import_profile(c,profile)
   self.assertEqual(display_adapter.export_profile(c),profile)
  invalid=copy.deepcopy(profile);invalid['devices'][0]['endpoint']='COM8';invalid['devices'].append(dict(self.body,window=999))
  with self.assertRaises(ValueError):
   with app.connect() as c:c.execute('BEGIN IMMEDIATE');display_adapter.import_profile(c,invalid)
  with app.connect() as c:self.assertEqual(display_adapter.export_profile(c),profile)
 def test_import_can_swap_addresses_without_losing_history(self):
  with app.connect() as c:
   display_adapter.save(c,dict(self.body,window=1,device_address='130'))
   display_adapter.save(c,dict(self.body,window=2,device_address='131'))
   saved=display_adapter.export_profile(c);saved['devices'][0]['device_address']='131';saved['devices'][1]['device_address']='130'
   ids=[r['id'] for r in display_adapter.state(c)['devices']];display_adapter.import_profile(c,saved)
   self.assertEqual([r['id'] for r in display_adapter.state(c)['devices']],ids)
   self.assertEqual([r['device_address'] for r in display_adapter.state(c)['devices']],['131','130'])
