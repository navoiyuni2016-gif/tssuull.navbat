[CmdletBinding()]
param([string]$AppPath='', [string]$Server='http://127.0.0.1:8080', [switch]$SkipRename, [switch]$NoStart)
$ErrorActionPreference='Stop'
if (-not $AppPath) {
    $running = @(Get-Process -Name TOShDOTAU -ErrorAction SilentlyContinue | ForEach-Object { try { Split-Path -Parent $_.Path } catch {} } | Select-Object -Unique)
    if ($running.Count -eq 1) { $AppPath = $running[0] }
    elseif ($running.Count -gt 1) { $AppPath = Read-Host 'Bir nechta nusxa bor. Kerakli TOShDOTAU.exe papka yolini kiriting' }
    elseif ($env:LOCALAPPDATA) {
        $candidate = Join-Path $env:LOCALAPPDATA 'Programs\TOShDOTAU'
        if (Test-Path -LiteralPath (Join-Path $candidate 'TOShDOTAU.exe')) { $AppPath = $candidate }
    }
    if (-not $AppPath) { $AppPath = Read-Host 'TOShDOTAU.exe turgan papka yolini kiriting' }
}

$appRoot=(Resolve-Path -LiteralPath $AppPath).ProviderPath
$webRoot=Join-Path $appRoot '_internal/web'
if (-not (Test-Path -LiteralPath (Join-Path $webRoot 'app.js'))) { $webRoot=Join-Path $appRoot 'web' }
$printerTarget=Join-Path $appRoot '_internal/windows/print-ticket.ps1'
if (-not (Test-Path -LiteralPath $printerTarget)) { $printerTarget=Join-Path $appRoot 'windows/print-ticket.ps1' }
foreach ($file in @((Join-Path $webRoot 'app.js'),(Join-Path $webRoot 'recordings.js'),$printerTarget)) {
  if (-not (Test-Path -LiteralPath $file)) { throw "Ilova fayli topilmadi: $file" }
}
# Verify the complete bundle before either updater changes anything.
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'bundle.json') -Raw | ConvertFrom-Json
foreach ($entry in $manifest.files) {
  if ((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $entry.path) -Algorithm SHA256).Hash -ne $entry.sha256) { throw "Patch SHA256 mos emas: $($entry.path)" }
}
$audio=Join-Path $PSScriptRoot 'audio/Update-Audio.ps1'
$receipt=Join-Path $PSScriptRoot 'receipt/Update-Receipt.ps1'
try {
  & $audio -AppPath $appRoot -Server $Server -SkipRename:$SkipRename -NoStart
  & $receipt -AppPath $appRoot -NoStart
} catch {
  Write-Host 'Yangilash toliq tugamadi. Ilova qayta ochilmadi. Zaxiralar saqlandi; xatoni tuzatib ayni buyruqni qayta bajaring.' -ForegroundColor Yellow
  throw
}
Write-Host 'TAYYOR: ovozlar va chek tuzatmasi birga ornatildi. C -> S tekshiruvi bajarildi (SkipRename tanlanmasa).' -ForegroundColor Green
$exe=Join-Path $appRoot 'TOShDOTAU.exe'
if (-not $NoStart -and (Test-Path -LiteralPath $exe)) { Start-Process -FilePath $exe }
