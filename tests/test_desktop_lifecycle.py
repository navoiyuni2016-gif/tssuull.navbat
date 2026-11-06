import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import app
from desktop_launcher import ServerSession
from native_window import admin_password_ok

class DesktopLifecycle(unittest.TestCase):
    def test_owned_server_closes_restarts_and_preserves_data(self):
        with tempfile.TemporaryDirectory() as folder:
            previous=app.DATA;app.DATA=Path(folder);app.initialize('desktop-lifecycle-password-123')
            with socket.socket() as reservation:reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
            session=ServerSession(app.DATA,port)
            try:
                session.start();app.issue(1,'desktop-lifecycle-ticket-123')
                with self.assertRaises(RuntimeError):ServerSession(app.DATA,port).start()
                session.close();self.assertFalse(session.thread.is_alive())
                session=ServerSession(app.DATA,port);session.start()
                with app.connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],1)
                self.assertTrue(admin_password_ok('admin','desktop-lifecycle-password-123'));self.assertFalse(admin_password_ok('admin','bad-password'))
            finally:session.close();app.DATA=previous
