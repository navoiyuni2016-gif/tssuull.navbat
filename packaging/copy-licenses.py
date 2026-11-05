"""Preserve redistribution notices alongside the bundled Python application."""
import importlib.metadata
from pathlib import Path
import shutil
import sys

output=Path(sys.argv[1]);output.mkdir(parents=True,exist_ok=True)
python_license=Path(sys.base_prefix)/'LICENSE.txt'
if not python_license.is_file():raise FileNotFoundError(python_license)
shutil.copyfile(python_license,output/'LICENSE-Python.txt')
distribution=importlib.metadata.distribution('pyinstaller')
license=next(distribution.locate_file(f) for f in distribution.files if str(f).endswith('licenses/COPYING.txt'))
shutil.copyfile(license,output/'LICENSE-PyInstaller.txt')
for license in (Path(sys.base_prefix)/'tcl').rglob('license.terms'):
    shutil.copyfile(license,output/(license.parent.name+'-license.terms'))
