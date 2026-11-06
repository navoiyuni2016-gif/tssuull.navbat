Unicode true
!include "MUI2.nsh"
Name "TOŞDÖTAU — elektron navbat"
OutFile "..\dist\TOShDOTAU-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\TOShDOTAU"
RequestExecutionLevel user
SetCompressor /SOLID lzma
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\TOShDOTAU.exe"
!define MUI_FINISHPAGE_RUN_TEXT "TOŞDÖTAU ilovasini ochish"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
Section "TOShDOTAU (majburiy)" Main
  SectionIn RO
  SetOutPath "$INSTDIR"
  File /r "..\dist\TOShDOTAU\*"
  CreateDirectory "$SMPROGRAMS\TOShDOTAU"
  CreateShortcut "$SMPROGRAMS\TOShDOTAU\TOShDOTAU.lnk" "$INSTDIR\TOShDOTAU.exe"
  CreateShortcut "$DESKTOP\TOShDOTAU.lnk" "$INSTDIR\TOShDOTAU.exe"
  CreateShortcut "$SMPROGRAMS\TOShDOTAU\Sozlamalar.lnk" "$INSTDIR\TOShDOTAU.exe" "--manage"
  ReadRegStr $0 HKCU "Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" "pv"
  StrCmp $0 "" check_machine runtime_done
  check_machine:
  SetRegView 32
  ReadRegStr $0 HKLM "Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" "pv"
  StrCmp $0 "" install_runtime runtime_done
  install_runtime:
  DetailPrint "Installing Microsoft WebView2 Runtime (internet may be required)..."
  ExecWait '"$INSTDIR\WebView2Setup.exe" /silent /install' $1
  IntCmp $1 0 runtime_done
  MessageBox MB_OK "WebView2 Runtime ornatilmadi. Internet bilan WebView2Setup.exe ni oching. WEBVIEW2_RUNTIME.md yoriqnomasiga qarang."
  runtime_done:
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TOShDOTAU" "DisplayName" "TOShDOTAU elektron navbat"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TOShDOTAU" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TOShDOTAU" "InstallLocation" "$INSTDIR"
SectionEnd
Section /o "Windowsga kirganda terminalni avtomatik ochish" Startup
  CreateShortcut "$SMSTARTUP\TOShDOTAU.lnk" "$INSTDIR\TOShDOTAU.exe" "--kiosk"
SectionEnd
Section "Uninstall"
  MessageBox MB_OKCANCEL "Ilova va serverni avval yoping. Baza va ovozlar saqlanadi." IDOK proceed
  Abort
  proceed:
  Delete "$SMSTARTUP\TOShDOTAU.lnk"
  Delete "$DESKTOP\TOShDOTAU.lnk"
  RMDir /r "$SMPROGRAMS\TOShDOTAU"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TOShDOTAU"
  Delete "$INSTDIR\TOShDOTAU.exe"
  RMDir /r "$INSTDIR\_internal"
  RMDir /r "$INSTDIR\licenses"
  Delete "$INSTDIR\WebView2Setup.exe"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
SectionEnd
