"""Package only source/guide files; never include DBs, sessions or local uploads."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
FILES=['app.py','alphabet.py','audio_store.py','management.py','printer_adapter.py','runtime.py','windows_service.py','report_exports.py','report_pdf.py','BOSHLASH.cmd','PRINTERNI_SOZLASH.cmd','README.md','VALIDATION.md','YO_RIQNOMA.html']
DIRECTORIES=['web','windows','tests','tools','fonts']
SUFFIXES={'.py','.js','.css','.html','.ps1','.md','.cmd','.svg','.png','.jpg','.jpeg','.ttf','.txt'}

def build(destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    selected=[ROOT/name for name in FILES]
    for name in DIRECTORIES:
        selected += [p for p in (ROOT/name).rglob('*') if p.is_file() and p.suffix in SUFFIXES and '__pycache__' not in p.parts]
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as output:
        for file in sorted(set(selected)):
            if file.is_symlink():raise ValueError('Symlinks are not packaged')
            output.write(file,'UniversitetNavbat/'+str(file.relative_to(ROOT)).replace('\\','/'))
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert not any('/data/' in n or '/.git/' in n or n.endswith(('.db','.env')) for n in archive.namelist())
    digest=hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix('.sha256').write_text(digest+'  '+destination.name+'\n')
    print(str(destination));print(f'{destination.stat().st_size} bytes; SHA256 {digest}')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT.parent/'artifacts'/'UniversitetNavbat.zip')
    build(parser.parse_args().output)
