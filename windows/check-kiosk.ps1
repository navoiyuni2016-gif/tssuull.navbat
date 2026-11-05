$ErrorActionPreference='Stop'
$windows=Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
Write-Host ('Windows: '+$windows.ProductName)
Write-Host ('Nashr: '+$windows.EditionID)
Write-Host ('Build: '+$windows.CurrentBuildNumber)
Write-Host ('Server xizmati: '+[bool](Get-Service UniversitetNavbat -ErrorAction SilentlyContinue))
Write-Host 'Pro / Enterprise / Education: Settings > Accounts > Other users > Set up a kiosk.'
Write-Host 'Home: Assigned Access mavjud emas. Faqat fullscreen boshqa dasturlarni bloklamaydi.'
Start-Process 'ms-settings:otherusers'
Read-Host 'Yopish uchun Enter'
