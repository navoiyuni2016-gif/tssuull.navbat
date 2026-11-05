"""Offline restore. Run from the project root: python tools/restore.py backup.db"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app
import runtime
import sqlite3

if len(sys.argv)!=2:raise SystemExit('Ishlatish: python tools/restore.py nusxa.db')
source=Path(sys.argv[1]).resolve()
if not source.is_file() or source==app.DATA.resolve()/'queue.db':raise SystemExit('Boshqa zaxira faylini tanlang')
with runtime.InstanceLock(app.DATA):
    with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as backup:
        if backup.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise SystemExit('Zaxira buzilgan')
        if backup.execute('PRAGMA user_version').fetchone()[0] not in (1,2,3):raise SystemExit('Zaxira versiyasi mos emas')
        if not backup.execute("SELECT 1 FROM sqlite_master WHERE name='tickets'").fetchone():raise SystemExit('Navbat bazasi emas')
        if (app.DATA/'queue.db').exists():print('Eski baza nusxasi:',runtime.backup(app.connect,app.DATA))
        with app.connect() as target:backup.backup(target)
    app.initialize()
print('Baza tiklandi. Audio fayllar uchun data/audio papkasini ham o‘z zaxirasidan tiklang.')
