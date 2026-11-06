import socket
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import app,display_adapter,display_protocol as protocol

class Protocol(unittest.TestCase):
 def device(self):return dict(window=5,device_address='130',transport='tcp',endpoint='127.0.0.1',enabled=True,profile=dict(protocol='manual_hex',tcp_port=1,timeout_ms=1000,show_template='02 {address8} {label_ascii} {xor8} 03',clear_template='02 {address8} 20 20 20 20 {xor8} 03'))
 def test_explicit_tokens_and_independent_checksum_vectors(self):
  d=self.device();self.assertEqual(protocol.frame(d['profile']['show_template'],d,'A001',5).hex(),'028241303031f003')
  self.assertEqual(protocol.frame('31 32 33 34 35 36 37 38 39 {modbus16}',d,'A001',5).hex(),'313233343536373839374b')
  self.assertEqual(protocol.frame('31 32 33 34 35 36 37 38 39 {sum8}',d,'A001',5)[-1],0xdd)
  self.assertEqual(protocol.frame('{label_ascii}',d,'B025',5),b'B025')
  self.assertEqual(protocol.frame('{number_ascii}',d,'B025',5),b'025')
 def test_invalid_or_incomplete_frames_do_not_send(self):
  d=self.device()
  for t in ['', 'GG', '0','{unknown}','{__import__}', 'AA'*513]:
   with self.assertRaises(ValueError):protocol.frame(t,d,'A001',5)
  d['profile']['clear_template']='{label_ascii}'
  with self.assertRaises(ValueError):protocol.prepare(d,'A001','clear')
  d=self.device();d['profile']['timeout_ms']=None
  with self.assertRaises(ValueError):protocol.prepare(d,'A001','show')
 def test_tcp_writes_only_requested_bytes_to_synthetic_receiver(self):
  # A test listener, never the user's LED hardware.
  with socket.socket() as server:
   server.bind(('127.0.0.1',0));server.listen();server.settimeout(3);received=[]
   def listen():
    c,_=server.accept()
    with c:received.append(c.recv(512))
   thread=threading.Thread(target=listen);thread.start();d=self.device();d['profile']['tcp_port']=server.getsockname()[1]
   protocol.send(d,b'UNIT-TEST');thread.join(timeout=4);self.assertEqual(received,[b'UNIT-TEST'])
 def test_serial_uses_exact_manual_parameters_with_fake_port(self):
  d=self.device();d['transport']='serial';d['endpoint']='COM2';d['profile'].update(baud_rate=19200,data_bits=7,parity='E',stop_bits='2')
  seen={}
  class Port:
   out_waiting=0
   def __init__(self,*args,**kwargs):seen.update(args=args,kwargs=kwargs)
   def write(self,data):seen['data']=data;return len(data)
   def close(self):seen['closed']=True
  with patch.dict('sys.modules',{'serial':SimpleNamespace(Serial=Port,SerialException=RuntimeError)}):protocol.send(d,b'FRAME')
  self.assertEqual(seen['args'],('COM2',));self.assertEqual(seen['kwargs']['baudrate'],19200);self.assertEqual(seen['kwargs']['bytesize'],7);self.assertEqual(seen['kwargs']['parity'],'E');self.assertEqual(seen['kwargs']['stopbits'],2);self.assertTrue(seen['closed'])
 def test_outbox_real_path_errors_do_not_replay_or_change_other_windows(self):
  old=app.DATA
  with tempfile.TemporaryDirectory() as folder:
   app.DATA=Path(folder)
   try:
    app.initialize('manual-led-test-password-123')
    with app.connect() as c:display_adapter.save(c,self.device())
    ticket=app.issue(1,'manual-led-outbox-request');app.action({'name':'admin','role':'admin','window':5},'next')
    sent=[]
    def sender(d,p):sent.append((d['window'],p));raise protocol.SendError('Test timeout',True)
    w=display_adapter.Worker(app.connect,sender=sender)
    with self.assertLogs('navbat',level='ERROR'):self.assertTrue(w.once())
    self.assertFalse(w.once());self.assertEqual(len(sent),1);self.assertEqual(sent[0][0],5)
    with app.connect() as c:
     self.assertEqual(c.execute('SELECT status FROM display_jobs').fetchone()[0],'uncertain')
     self.assertEqual(c.execute('SELECT status FROM tickets WHERE id=?',(ticket['id'],)).fetchone()[0],'called')
     self.assertEqual(c.execute('SELECT count(*) FROM calls').fetchone()[0],1)
   finally:app.DATA=old
