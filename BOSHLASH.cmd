@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 -c "import sys; assert sys.version_info >= (3,12)" >nul 2>&1
if errorlevel 1 (
 echo Python 3.12 yoki yangirog‘i kerak. python.org dan o‘rnating.
 pause
 exit /b 1
)
py -3 -c "import app,sys; c=app.connect(); sys.exit(0 if c.execute('SELECT count(*) FROM users').fetchone()[0] else 1)" >nul 2>&1
if errorlevel 1 (
 py -3 app.py --init
 if errorlevel 1 (
  pause
  exit /b 1
 )
)
start "Navbat brauzeri" powershell.exe -NoProfile -File "%~dp0windows\kiosk.ps1"
py -3 app.py --host 0.0.0.0 --port 8080
pause
