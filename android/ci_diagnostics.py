from pathlib import Path
import xml.etree.ElementTree as ET

def annotate(text):
    print('::error::'+text.replace('%','%25').replace('\r','%0D').replace('\n','%0A'))
for path in Path('android/app/build').rglob('*.xml'):
    try:
        for issue in ET.parse(path).getroot().iter():
            if issue.tag in ('failure','error'):annotate(str(path)+'\n'+(issue.text or issue.get('message',''))[-4000:])
    except (OSError,ET.ParseError):pass
for name in ('android/build.log','android/emulator.log'):
    path=Path(name)
    if path.exists():annotate(path.read_text(errors='replace')[-6000:])
