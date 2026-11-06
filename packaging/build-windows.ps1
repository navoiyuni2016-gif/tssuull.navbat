$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
python packaging/make_icon.py
if($LASTEXITCODE -ne 0){throw 'University icon conversion failed'}
python -m PyInstaller --noconfirm --clean --windowed --onedir --name TOShDOTAU --icon build/university.ico --add-data 'build/university.ico;.' --collect-all webview --hidden-import webview.platforms.winforms --hidden-import webview.platforms.edgechromium --collect-all pythonnet --collect-all clr_loader --add-data 'web;web' --add-data 'fonts;fonts' --add-data 'windows;windows' --add-data 'README.md;.' --add-data 'EXE_BOSHLASH.md;.' --add-data 'WEBVIEW2_RUNTIME.md;.' --add-data 'LED_TEXNIK_TAHLIL.md;.' --add-data 'LED_QOLDA_SOZLASH.md;.' desktop_launcher.py
if($LASTEXITCODE -ne 0){throw 'PyInstaller build failed'}
python packaging/copy-licenses.py dist/TOShDOTAU/licenses
if($LASTEXITCODE -ne 0){throw 'Runtime licenses missing'}
$env:NAVBAT_EXE=(Join-Path $PWD 'dist\TOShDOTAU\TOShDOTAU.exe')
python tools/ci_tests.py test_frozen_windows.py
if($LASTEXITCODE -ne 0){throw 'Frozen application verification failed'}
$runtime='dist/TOShDOTAU/WebView2Setup.exe'
Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile $runtime
$signature=Get-AuthenticodeSignature $runtime
if($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Microsoft Corporation'){throw 'WebView2 installer signature invalid'}
$nsis="${env:ProgramFiles(x86)}\NSIS\makensis.exe"
if(!(Test-Path $nsis)){throw 'NSIS not installed'}
& $nsis /V2 packaging/installer.nsi
if($LASTEXITCODE -ne 0){throw 'Installer build failed'}
Compress-Archive -Path dist/TOShDOTAU -DestinationPath dist/TOShDOTAU-Windows.zip -Force
Get-FileHash dist/TOShDOTAU-Setup.exe -Algorithm SHA256 | ForEach-Object {($_.Hash.ToLower()+'  TOShDOTAU-Setup.exe')} | Set-Content dist/SHA256SUMS.txt -Encoding ASCII
