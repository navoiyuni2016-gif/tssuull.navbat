param([string]$Server='http://127.0.0.1:8080')
$ErrorActionPreference='Stop'
$edge="${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
if (!(Test-Path $edge)) { $edge="$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe" }
for ($i=0; $i -lt 60; $i++) {
  try { $null=Invoke-RestMethod "$Server/api/state"; break } catch { Start-Sleep -Seconds 1 }
}
Start-Process $edge -ArgumentList @('--kiosk',$Server,'--edge-kiosk-type=fullscreen','--no-first-run')
