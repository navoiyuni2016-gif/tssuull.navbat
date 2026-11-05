"""Shared paths and instance identity for the Windows desktop distribution."""
import hashlib
import os
from pathlib import Path
import sqlite3
import sys


def data_directory():
    if os.environ.get('NAVBAT_DATA'):
        return Path(os.environ['NAVBAT_DATA']).resolve()
    return Path(os.environ.get('LOCALAPPDATA',Path.home()))/'TOShDOTAU'/'Navbat'/'data'


def instance_id(directory):
    return hashlib.sha256(os.path.normcase(str(Path(directory).resolve())).encode()).hexdigest()[:24]


def has_admin(directory):
    path=Path(directory)/'queue.db'
    if not path.is_file():return False
    try:
        with sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True) as c:
            return bool(c.execute('SELECT 1 FROM users LIMIT 1').fetchone())
    except sqlite3.OperationalError:return False


def launch_command(*args):
    if getattr(sys,'frozen',False):return [sys.executable,*args]
    return [sys.executable,str(Path(__file__).with_name('desktop_launcher.py')),*args]


def validate_password(value,confirmation):
    if len(value)<12:raise ValueError('Parol kamida 12 belgidan iborat bölsin.')
    if value!=confirmation:raise ValueError('Parollar bir xil emas.')
