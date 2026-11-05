import database
import tempfile
import unittest
from pathlib import Path
import sqlite3
import app
import runtime
from tools.prepare_install_data import copy_data

class InstallData(unittest.TestCase):
    def test_preserves_database_and_audio_without_overwriting(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);old=root/'old';new=root/'new';previous=app.DATA
            try:
                app.DATA=old;app.initialize('install-test-password-123');app.issue(1,'install-preserved-request-123')
                (old/'audio').mkdir();(old/'audio'/'sample.wav').write_bytes(b'fixture-audio')
                copy_data(old,new)
                with database.connect(new/'queue.db') as c:
                    self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],1)
                    self.assertEqual(c.execute('SELECT count(*) FROM users').fetchone()[0],1)
                self.assertEqual((new/'audio'/'sample.wav').read_bytes(),b'fixture-audio')
                with self.assertRaises(ValueError):copy_data(old,new)
                with runtime.InstanceLock(old):
                    with self.assertRaises(RuntimeError):copy_data(old,root/'blocked')
                self.assertFalse((root/'blocked').exists())
            finally:app.DATA=previous
