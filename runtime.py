"""Automatic consistent backups; keep the newest fourteen daily snapshots."""
import datetime as dt
import logging
import sqlite3
import threading


def backup(connect,data):
    destination=data/'backups';destination.mkdir(exist_ok=True)
    path=destination/(dt.datetime.now(dt.timezone(dt.timedelta(hours=5))).strftime('%Y%m%d-%H%M%S-%f')+'.db')
    with connect() as source,sqlite3.connect(path) as target:source.backup(target)
    return path


def start_backups(connect,data):
    def run():
        day=None
        while True:
            try:
                today=dt.datetime.now(dt.timezone(dt.timedelta(hours=5))).date()
                if today!=day:
                    backup(connect,data);day=today
                    for old in sorted((data/'backups').glob('*.db'),reverse=True)[14:]:old.unlink()
            except Exception:logging.getLogger('navbat').exception('Zaxira xatosi')
            threading.Event().wait(60)
    threading.Thread(target=run,daemon=True).start()


class InstanceLock:
    """Prevent two servers/restore processes from operating on the same data."""
    def __init__(self,data):self.data=data;self.stream=None
    def __enter__(self):
        self.data.mkdir(parents=True,exist_ok=True)
        self.stream=(self.data/'server.lock').open('a+b')
        self.stream.seek(0,2)
        if self.stream.tell()==0:self.stream.write(b'0');self.stream.flush()
        self.stream.seek(0)
        try:
            import os
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as error:
            self.stream.close();raise RuntimeError('Server ishlab turibdi. Avval uni to‘xtating.') from error
        return self
    def __exit__(self,*args):
        self.stream.close()
