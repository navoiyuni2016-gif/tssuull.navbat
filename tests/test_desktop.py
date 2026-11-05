import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import app
import desktop_runtime as desktop

class Desktop(unittest.TestCase):
    def test_first_run_and_existing_admin(self):
        with tempfile.TemporaryDirectory() as folder:
            data=Path(folder)/'data';previous=app.DATA
            self.assertFalse(desktop.has_admin(data));self.assertFalse(data.exists())
            try:
                app.DATA=data;app.initialize('desktop-test-password-123');self.assertTrue(desktop.has_admin(data))
            finally:app.DATA=previous
    def test_data_path_and_instance_identity(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'NAVBAT_DATA':folder}):
            self.assertEqual(desktop.data_directory(),Path(folder).resolve())
            self.assertEqual(desktop.instance_id(folder),desktop.instance_id(Path(folder)/'.'))
            self.assertNotEqual(desktop.instance_id(folder),desktop.instance_id(Path(folder)/'other'))
    def test_password_confirmation(self):
        with self.assertRaises(ValueError):desktop.validate_password('short','short')
        with self.assertRaises(ValueError):desktop.validate_password('a-long-password','a-different-password')
        desktop.validate_password('valid-password-123','valid-password-123')
