@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 app.py --configure-printer "KPOS_80 Printer(1)"
if errorlevel 1 (
 echo Printer sozlanmadi. Windows drayverini tekshiring.
) else (
 echo Tayyor. Terminal sahifasini Ctrl+F5 bilan yangilang.
)
pause
