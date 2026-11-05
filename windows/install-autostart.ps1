param([int]$Port=8080,[string]$BindAddress='0.0.0.0',[string]$InstallPath="$env:ProgramData\UniversitetNavbat")
$ErrorActionPreference='Stop'
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if (!(New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {throw 'PowerŞell oynasini administrator sifatida oçing'}
if ($Port -lt 1024 -or $Port -gt 65535) {throw 'Port 1024–65535 oraliğida bölsin'}
$source=Split-Path $PSScriptRoot -Parent
if (Get-Service UniversitetNavbat -ErrorAction SilentlyContinue) {throw 'Xizmat mavjud. Yangilaşdan oldin xizmatni töxtating va zaxira oling; mavjud örnatiş ustiga yozilmadi.'}
$python=(& py -3 -c 'import sys; print(sys.executable)')
if ($LASTEXITCODE -ne 0) {throw 'Python 3.12 yoki yangiroğini barça foydalanuvçilar uçun örnating'}
if (Test-Path $InstallPath) {throw 'Örnatiş papkasi mavjud. Maʼlumotlarni saqlab, boşqa InstallPath tanlang.'}
New-Item -ItemType Directory -Path $InstallPath | Out-Null
foreach($item in @('app.py','management.py','audio_store.py','runtime.py','printer_adapter.py','windows_service.py','report_exports.py','report_pdf.py','fonts','alphabet.py','web','windows','tools','README.md','KIOSK_VA_TV.md','BOSHLASH.cmd','PRINTERNI_SOZLASH.cmd','YO_RIQNOMA.html')) {
  Copy-Item -LiteralPath (Join-Path $source $item) -Destination $InstallPath -Recurse
}
$config=@{host=$BindAddress;port=$Port}|ConvertTo-Json
[IO.File]::WriteAllText((Join-Path $InstallPath 'windows\server.json'),$config,(New-Object Text.UTF8Encoding($false)))
Push-Location $InstallPath
try {
  $existingData=Join-Path $source 'data'
  if(Test-Path (Join-Path $existingData 'queue.db')) {
    & $python tools/prepare_install_data.py $existingData (Join-Path $InstallPath 'data')
    if($LASTEXITCODE -ne 0){throw 'Eski serverni toxtating. Baza kochmadi; eski fayllar ozgarmadi.'}
    & $python -c 'import app; app.initialize()'
  } else { & $python app.py --init }
  if($LASTEXITCODE -ne 0){throw 'Baza tayyorlanmadi'}
} finally {Pop-Location}
# LocalService only needs write access to data, not application source.
& icacls.exe (Join-Path $InstallPath 'data') /grant '*S-1-5-19:(OI)(CI)M' | Out-Null
if($LASTEXITCODE -ne 0){throw 'Data papkasi ruxsatini sozlab bölmadi'}
$bin='"'+$python+'" "'+(Join-Path $InstallPath 'windows_service.py')+'"'
& sc.exe create UniversitetNavbat binPath= $bin start= auto obj= 'NT AUTHORITY\LocalService' DisplayName= 'Universitet elektron navbat'
if($LASTEXITCODE -ne 0){throw 'Windows xizmati yaratilmadi'}
& sc.exe failure UniversitetNavbat reset= 86400 actions= 'restart/5000/restart/15000/restart/60000'
New-NetFirewallRule -Name 'UniversitetNavbatLAN' -DisplayName 'Universitet Navbat — lokal tarmoq' -Direction Inbound -Action Allow -Protocol TCP -LocalPort $Port -Profile Private -RemoteAddress LocalSubnet | Out-Null
Start-Service UniversitetNavbat
$kiosk=Join-Path $InstallPath 'windows\kiosk.ps1'
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -File "'+$kiosk+'" -Server "http://127.0.0.1:'+$Port+'"')
$trigger=New-ScheduledTaskTrigger -AtLogOn -User $identity.Name
$displaySettings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew
Register-ScheduledTask -Settings $displaySettings -TaskName 'UniversitetNavbatKiosk' -Action $action -Trigger $trigger -User $identity.Name -Description 'Terminal foydalanuvçisi kirganda kiosk' | Out-Null
Write-Host 'Xizmat va kiosk avtomatik işga tuşişi sozlandi. Kompyuterni qayta yoqib, printer va tarmoqni sinang.'
Write-Host 'Windows printeri LocalService hisobiga ham örnatilgan bölişi kerak. Faqat sizga örnatilgan printer xizmatda körinmasligi mumkin.'
