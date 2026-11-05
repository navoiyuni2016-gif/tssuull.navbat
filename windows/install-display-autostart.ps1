param(
  [string]$Server='http://127.0.0.1:8080',
  [ValidateSet('Terminal','TV')][string]$Mode='Terminal'
)
$ErrorActionPreference='Stop'
$uri=$null
if (![Uri]::TryCreate($Server,[UriKind]::Absolute,[ref]$uri) -or $uri.Scheme -notin @('http','https') -or $uri.UserInfo -or $uri.Query -or $uri.Fragment) {throw 'Server manzilini tekshiring'}
$script=Join-Path $PSScriptRoot 'kiosk.ps1'
$user=[Security.Principal.WindowsIdentity]::GetCurrent().Name
$name='UniversitetNavbatDisplay'+$Mode
$arguments='-NoProfile -WindowStyle Hidden -File "'+$script+'" -Server "'+$uri.GetLeftPart([UriPartial]::Authority)+'" -Mode '+$Mode
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arguments
$trigger=New-ScheduledTaskTrigger -AtLogOn -User $user
$principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $name
Write-Host 'Avtomatik toliq ekran sozlandi. Bu foydalanuvchi Windowsga kirganda ochiladi.'
Write-Host 'Boshqa dasturlarni cheklash va avtomatik kirish uchun Windows Assigned Access kiosk rejimini sozlang. Bu skript uni almashtirmaydi.'
