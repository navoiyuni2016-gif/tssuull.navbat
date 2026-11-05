param(
  [string]$Server='http://127.0.0.1:8080',
  [ValidateSet('Terminal','TV')][string]$Mode='Terminal'
)
$ErrorActionPreference='Stop'
$address=$null
if (![Uri]::TryCreate($Server,[UriKind]::Absolute,[ref]$address) -or $address.Scheme -notin @('http','https') -or $address.UserInfo -or $address.Query -or $address.Fragment) { throw 'Server manzili http://IP:8080 shaklida bolsin' }
$base=$address.GetLeftPart([UriPartial]::Authority)
$url=if($Mode -eq 'TV'){$base+'/tv?autostart=1'}else{$base+'/'}
$edge="${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
if (!(Test-Path $edge)) {$edge="$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"}
if (!(Test-Path $edge)) {throw 'Microsoft Edge topilmadi'}
$lock=New-Object Threading.Mutex($false,('Local\ToshdotauDisplay'+$Mode))
$owned=$false
try {
  try {$owned=$lock.WaitOne(0)} catch [Threading.AbandonedMutexException] {$owned=$true}
  if (!$owned) {return}
  $profile=Join-Path $env:LOCALAPPDATA ('UniversitetNavbat\Kiosk-'+$Mode)
  while ($true) {
    # Wait for the local server / LAN, including after power loss.
    $ready=$false
    while (!$ready) {
      try {$null=Invoke-RestMethod ($base+'/api/state') -TimeoutSec 5;$ready=$true}
      catch {Start-Sleep -Seconds 2}
    }
    Start-Process -FilePath $edge -ArgumentList @('--kiosk',('"'+$url+'"'),'--edge-kiosk-type=fullscreen','--no-first-run',('--user-data-dir="'+$profile+'"')) -Wait
    Start-Sleep -Seconds 2
  }
} finally {
  if($owned){$lock.ReleaseMutex()}
  $lock.Dispose()
}
