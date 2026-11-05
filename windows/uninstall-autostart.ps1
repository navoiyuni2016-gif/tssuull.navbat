$ErrorActionPreference='Stop'
if(Get-Service UniversitetNavbat -ErrorAction SilentlyContinue){Stop-Service UniversitetNavbat; & sc.exe delete UniversitetNavbat}
Unregister-ScheduledTask -TaskName 'UniversitetNavbatKiosk' -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName 'UniversitetNavbatDisplayTerminal' -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName 'UniversitetNavbatDisplayTV' -Confirm:$false -ErrorAction SilentlyContinue
Remove-NetFirewallRule -Name 'UniversitetNavbatLAN' -ErrorAction SilentlyContinue
Write-Host 'Avtomatik işga tuşiriş olib taşlandi. Loyiha, baza va ovoz fayllari saqlandi.'
