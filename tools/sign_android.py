"""Sign a tested Android build with an owner-controlled key kept outside Git."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile


def sign(source,destination,jar,keystore,password_file):
    source=Path(source);destination=Path(destination)
    if source.resolve()==destination.resolve():raise ValueError('Input and signed output must differ')
    for path in (source,Path(jar),Path(keystore),Path(password_file)):
        if not path.is_file():raise FileNotFoundError(path)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as directory:
        output=Path(directory)/'signed.apk'
        subprocess.run(['java','-jar',str(jar),'sign','--ks',str(keystore),'--ks-key-alias','toshdotau-tv','--ks-pass','file:'+str(password_file),'--v1-signing-enabled','true','--v2-signing-enabled','true','--v3-signing-enabled','true','--v4-signing-enabled','false','--out',str(output),str(source)],check=True)
        verified=subprocess.run(['java','-jar',str(jar),'verify','--min-sdk-version','21','--verbose','--print-certs',str(output)],capture_output=True,text=True,check=True)
        output.replace(destination)
    destination.with_suffix('.apk.sha256').write_text(hashlib.sha256(destination.read_bytes()).hexdigest()+'  '+destination.name+'\n',encoding='ascii')
    destination.with_suffix('.certificate.txt').write_text(verified.stdout,encoding='utf-8')
    print(verified.stdout,end='');print('Signed APK:',destination)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ('input','output','apksigner','keystore','password-file'):parser.add_argument('--'+name,required=True,type=Path)
    args=parser.parse_args();sign(args.input,args.output,args.apksigner,args.keystore,args.password_file)
