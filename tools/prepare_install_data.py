"""Copy an existing stopped installation into a new service installation."""
from pathlib import Path
import shutil
import sqlite3
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import database
import runtime


def copy_data(source,destination):
    source=Path(source).resolve();destination=Path(destination).resolve()
    db_file=source/'queue.db'
    if not db_file.is_file():raise ValueError('Eski queue.db topilmadi')
    if destination.exists():raise ValueError('Yangi data papkasi allaqachon mavjud; ustidan yozilmadi')
    audio=source/'audio'
    if audio.exists() and (audio.is_symlink() or any(p.is_symlink() for p in audio.rglob('*'))):
        raise ValueError('Audio papkasida symlink bor; qolda tekshiring')
    with runtime.InstanceLock(source):
        with database.connect(db_file.as_uri()+'?mode=ro',uri=True) as old:
            if old.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Eski baza yaxlitligi xato')
            if not old.execute('SELECT count(*) FROM users').fetchone()[0]:raise ValueError('Eski administrator topilmadi')
            destination.mkdir(parents=True)
            with database.connect(destination/'queue.db') as new:old.backup(new)
        if audio.exists():shutil.copytree(audio,destination/'audio')

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('python tools/prepare_install_data.py OLD_DATA NEW_DATA')
    copy_data(*sys.argv[1:]);print('Baza, loginlar, sozlamalar va ovozlar yangi ornatishga kochirildi.')
