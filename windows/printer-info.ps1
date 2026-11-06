$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.Encoding]::UTF8
Add-Type -AssemblyName System.Drawing
$details=@(Get-CimInstance Win32_Printer -ErrorAction SilentlyContinue)
$printers=@(foreach($name in [Drawing.Printing.PrinterSettings]::InstalledPrinters){
  $item=$details | Where-Object {$_.Name -eq $name} | Select-Object -First 1
  @{name=[string]$name;driver=[string]$item.DriverName;port=[string]$item.PortName;offline=[bool]$item.WorkOffline;status=[int]$item.PrinterStatus}
})
@{account=[Security.Principal.WindowsIdentity]::GetCurrent().Name;spooler=[string](Get-Service Spooler).Status;printers=$printers}|ConvertTo-Json -Depth 5 -Compress
