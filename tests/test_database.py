import tempfile
from pathlib import Path
import sqlite3
import unittest
import database

class DatabaseHandles(unittest.TestCase):
    def test_commit_rollback_and_immediate_close(self):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'test.db'
            with database.connect(file) as c:
                c.execute('CREATE TABLE items(value TEXT)');c.execute("INSERT INTO items VALUES ('kept')")
            with self.assertRaises(sqlite3.ProgrammingError):c.execute('SELECT 1')
            with self.assertRaises(ValueError):
                with database.connect(file) as failed:
                    failed.execute("INSERT INTO items VALUES ('rolled back')");raise ValueError('rollback')
            with self.assertRaises(sqlite3.ProgrammingError):failed.execute('SELECT 1')
            with database.connect(file) as check:self.assertEqual(check.execute('SELECT value FROM items').fetchall(),[('kept',)])
            file.unlink() # Must succeed even while the closed connection objects are still referenced.
