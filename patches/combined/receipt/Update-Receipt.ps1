[CmdletBinding()]
param([string]$AppPath='', [switch]$Restore, [switch]$NoStart)
$ErrorActionPreference='Stop'
function Get-AppProcesses([string]$root) {
  @(Get-Process -Name TOShDOTAU -ErrorAction SilentlyContinue | Where-Object { try { (Split-Path -Parent $_.Path) -eq $root } catch { $false } })
}
if (-not $AppPath) {
  $running=@(Get-Process -Name TOShDOTAU -ErrorAction SilentlyContinue | ForEach-Object { try { Split-Path -Parent $_.Path } catch {} } | Select-Object -Unique)
  if ($running.Count -eq 1) { $AppPath=$running[0] }
  elseif ($running.Count -gt 1) { $AppPath=Read-Host 'Kerakli TOShDOTAU.exe papka yolini kiriting' }
  elseif ($env:LOCALAPPDATA) {
    $candidate=Join-Path $env:LOCALAPPDATA 'Programs\TOShDOTAU'
    if (Test-Path -LiteralPath (Join-Path $candidate 'TOShDOTAU.exe')) { $AppPath=$candidate }
  }
  if (-not $AppPath) { $AppPath=Read-Host 'TOShDOTAU.exe turgan papka yolini kiriting' }
}
$root=(Resolve-Path -LiteralPath $AppPath).ProviderPath
$target=Join-Path $root '_internal/windows/print-ticket.ps1'
if (-not (Test-Path -LiteralPath $target)) { $target=Join-Path $root 'windows/print-ticket.ps1' }
if (-not (Test-Path -LiteralPath $target)) { throw 'Printer skripti topilmadi. EXE papkasini tekshiring.' }
$source=Join-Path $PSScriptRoot 'windows/print-ticket.ps1'
$expected='c12bb9d49735433795eac49ae748b83d1a3150eee19701484474e45d53a3ed1c'
if (-not $Restore -and (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $expected) { throw 'Patch SHA256 mos emas' }
$backupRoot=Join-Path $root 'receipt-patch-backups'
if (@(Get-AppProcesses $root).Count) {
  Write-Host 'Avval navbat ilovasini odatdagi admin paroli bilan yoping. Jarayon majburan toxtatilmaydi.' -ForegroundColor Yellow
  $null=Read-Host 'Yopilgach Enter bosing'
  if (@(Get-AppProcesses $root).Count) { throw 'Ilova hali ochiq. Yopib qayta urining.' }
}
if ($Restore) {
  $backup=Get-ChildItem -LiteralPath $backupRoot -File | Where-Object { $_.Name -like 'print-ticket-*.ps1' } | Sort-Object Name -Descending | Select-Object -First 1
  if (-not $backup) { throw 'Zaxira topilmadi' }
  $source=$backup.FullName
} elseif ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -eq $expected) {
  Write-Host 'Chek patchi allaqachon ornatilgan.'
  if (-not $NoStart -and (Test-Path -LiteralPath (Join-Path $root 'TOShDOTAU.exe'))) { Start-Process -FilePath (Join-Path $root 'TOShDOTAU.exe') }
  exit 0
}
$null=New-Item -ItemType Directory -Path $backupRoot -Force
if (-not $Restore) {
  $backup=Join-Path $backupRoot ('print-ticket-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff')+'.ps1')
  Copy-Item -LiteralPath $target -Destination $backup
}
$temporary=$target+'.receipt-new'
Copy-Item -LiteralPath $source -Destination $temporary -Force
$replaceBackup=$target+'.receipt-old'
[IO.File]::Replace($temporary,$target,$replaceBackup)
if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash) {
  Copy-Item -LiteralPath $replaceBackup -Destination $target -Force
  throw 'Kochirish tekshirilmadi; eski fayl qaytarildi'
}
Remove-Item -LiteralPath $replaceBackup -Force
Write-Host 'Chek bosma maydoniga moslashtirildi. EXE, baza, ovozlar va printer sozlamalari saqlandi.' -ForegroundColor Green
Write-Host 'Bitta sinov chekini chiqaring. Eski chiptalar avtomatik qayta chop etilmaydi.'
if (-not $NoStart -and (Test-Path -LiteralPath (Join-Path $root 'TOShDOTAU.exe'))) { Start-Process -FilePath (Join-Path $root 'TOShDOTAU.exe') }
