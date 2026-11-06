from pathlib import Path
from PIL import Image
Path('build').mkdir(exist_ok=True)
with Image.open('web/assets/university-logo.png') as logo:
    logo.convert('RGBA').save('build/university.ico',format='ICO',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
