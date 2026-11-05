import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import app
import runtime

class Runtime(unittest.TestCase):
    def test_exclusive_lock_and_offline_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            data=Path(directory);previous=app.DATA;app.DATA=data
            try:
                app.initialize('restore-test-password-123')
                with runtime.InstanceLock(data):
                    with self.assertRaises(RuntimeError):
                        with runtime.InstanceLock(data):pass
                first=app.issue(1,'restore-first-request-123')
                snapshot=runtime.backup(app.connect,data)
                app.issue(1,'restore-second-request-123')
                env=dict(os.environ,NAVBAT_DATA=str(data))
                completed=subprocess.run([sys.executable,'tools/restore.py',str(snapshot)],cwd=app.ROOT,env=env,capture_output=True,text=True,timeout=20)
                self.assertEqual(completed.returncode,0,completed.stderr)
                with app.connect() as c:
                    self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],1)
                    self.assertEqual(c.execute('SELECT id FROM tickets').fetchone()[0],first['id'])
                with runtime.InstanceLock(data):
                    blocked=subprocess.run([sys.executable,'tools/restore.py',str(snapshot)],cwd=app.ROOT,env=env,capture_output=True,text=True,timeout=20)
                    self.assertNotEqual(blocked.returncode,0)
            finally:app.DATA=previous
