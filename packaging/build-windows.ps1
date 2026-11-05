$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
python -m PyInstaller --noconfirm --clean --windowed --onedir --name TOShDOTAU --add-data 'web;web' --add-data 'fonts;fonts' --add-data 'windows;windows' --add-data 'README.md;.' --add-data 'EXE_BOSHLASH.md;.' desktop_launcher.py
if($LASTEXITCODE -ne 0){throw 'PyInstaller build failed'}
python packaging/copy-licenses.py dist/TOShDOTAU/licenses
if($LASTEXITCODE -ne 0){throw 'Runtime licenses missing'}
$env:NAVBAT_EXE=(Join-Path $PWD 'dist\TOShDOTAU\TOShDOTAU.exe')
python -m unittest discover -s tests -p test_frozen_windows.py -v
if($LASTEXITCODE -ne 0){throw 'Frozen application verification failed'}
$nsis="${env:ProgramFiles(x86)}\NSIS\makensis.exe"
if(!(Test-Path $nsis)){throw 'NSIS not installed'}
& $nsis /V2 packaging/installer.nsi
if($LASTEXITCODE -ne 0){throw 'Installer build failed'}
Compress-Archive -Path dist/TOShDOTAU -DestinationPath dist/TOShDOTAU-Windows.zip -Force
Get-FileHash dist/TOShDOTAU-Setup.exe -Algorithm SHA256 | ForEach-Object {($_.Hash.ToLower()+'  TOShDOTAU-Setup.exe')} | Set-Content dist/SHA256SUMS.txt -Encoding ASCII
