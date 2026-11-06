[CmdletBinding()]
param(
    [string]$AppPath = '',
    [string]$Server = 'http://127.0.0.1:8080',
    [switch]$SkipRename,
    [switch]$NoStart,
    [switch]$Restore
)
$ErrorActionPreference = 'Stop'
$patchRoot = $PSScriptRoot
$serverUri = [Uri]$Server
if ($serverUri.Scheme -ne 'http' -or $serverUri.Host -notin @('127.0.0.1','localhost') -or $serverUri.UserInfo -or $serverUri.AbsolutePath -ne '/') { throw 'Patch infokioskning ozida localhost server bilan ishlatiladi' }
$serverBase = $serverUri.GetLeftPart([UriPartial]::Authority)
function Get-AppProcesses([string]$root) {
    @(Get-Process -Name TOShDOTAU -ErrorAction SilentlyContinue | Where-Object {
        try { (Split-Path -Parent $_.Path) -eq $root } catch { $false }
    })
}
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
$appRoot = (Resolve-Path -LiteralPath $AppPath).ProviderPath
$exe = Join-Path $appRoot 'TOShDOTAU.exe'
$webRoot = Join-Path $appRoot '_internal/web'
if (-not (Test-Path -LiteralPath (Join-Path $webRoot 'app.js'))) { $webRoot = Join-Path $appRoot 'web' }
foreach ($name in @('app.js','recordings.js')) {
    if (-not (Test-Path -LiteralPath (Join-Path $webRoot $name))) { throw "Navbat web fayli topilmadi: $name. AppPath ni tekshiring." }
}
$backupRoot = Join-Path $appRoot 'audio-patch-backups'
if (-not $Restore) {
    $manifest = Get-Content -LiteralPath (Join-Path $patchRoot 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.version -ne 1 -or @($manifest.files).Count -ne 2) { throw 'Patch manifesti notogri' }
    $seen = @{}
    foreach ($entry in $manifest.files) {
        if ($entry.name -notin @('app.js','recordings.js') -or $seen.ContainsKey($entry.name)) { throw 'Patch fayl nomi notogri' }
        $seen[$entry.name] = $true
        $source = Join-Path (Join-Path $patchRoot 'web') $entry.name
        if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $entry.sha256) { throw "SHA256 mos emas: $($entry.name)" }
    }
    # Business prefix edit uses the existing authenticated API; never edits SQLite.
    if (-not $SkipRename) {
        try { $state = Invoke-RestMethod "$serverBase/api/state" -TimeoutSec 5 }
        catch { throw 'C -> S uchun navbat ilovasini avval oching va skriptni qayta ishga tushiring. -SkipRename faqat ovoz patchini ornatadi.' }
        $targets = @($state.services | Where-Object { $_.prefix -eq 'C' })
        if ($targets.Count -gt 1) { throw 'Bir nechta C bolimi bor; administrator panelidan tekshiring' }
        if ($targets.Count -eq 1) {
            if (@($state.services | Where-Object { $_.prefix -eq 'S' }).Count) { throw 'S harfi boshqa bolimga berilgan. Avval Xizmatlar panelida tekshiring.' }
            $credential = Get-Credential -UserName 'admin' -Message 'C -> S uchun mavjud administrator login va parolini kiriting'
            if (-not $credential) { throw 'Administrator kirishi bekor qilindi' }
            $login = @{ name=$credential.UserName; password=$credential.GetNetworkCredential().Password } | ConvertTo-Json -Compress
            try { $null = Invoke-RestMethod "$serverBase/api/login" -Method Post -ContentType 'application/json' -Body ([Text.Encoding]::UTF8.GetBytes($login)) -SessionVariable session -TimeoutSec 10 }
            finally { $login=$null; $credential=$null }
            try {
                $admin = Invoke-RestMethod "$serverBase/api/admin" -WebSession $session -TimeoutSec 10
                $service = @($admin.services | Where-Object { $_.id -eq $targets[0].id })[0]
                if ($service.prefix -ne 'C') { throw 'Bolim boshqa oynada ozgartirilgan; qayta tekshiring' }
                $null = New-Item -ItemType Directory -Path $backupRoot -Force
                $beforeFile = Join-Path $backupRoot ('prefix-before-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
                $service | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $beforeFile -Encoding UTF8
                $body = @{ id=[int]$service.id; name=$service.name; name_en=$service.name_en; name_ru=$service.name_ru; prefix='S'; enabled=[bool]$service.enabled } | ConvertTo-Json -Compress
                $null = Invoke-RestMethod "$serverBase/api/services" -Method Post -ContentType 'application/json' -Body ([Text.Encoding]::UTF8.GetBytes($body)) -WebSession $session -TimeoutSec 10
                Write-Host 'C -> S saqlandi. Eski chiptalar va tarix ozgarmadi.' -ForegroundColor Green
            } finally { try { $null=Invoke-RestMethod "$serverBase/api/logout" -Method Post -ContentType 'application/json' -Body '{}' -WebSession $session -TimeoutSec 5 } catch {} }
        } else { Write-Host 'C prefiksi topilmadi. Harflar ozgartirilmadi; ovoz patchi davom etadi.' }
    }
}
if (@(Get-AppProcesses $appRoot).Count) {
    Write-Host 'TOShDOTAU ilovasini odatdagi usulda admin paroli bilan yoping. Jarayon majburan toxtatilmaydi.' -ForegroundColor Yellow
    $null = Read-Host 'Yopilgach Enter bosing'
    for ($i=0; $i -lt 30 -and @(Get-AppProcesses $appRoot).Count; $i++) { Start-Sleep -Milliseconds 500 }
    if (@(Get-AppProcesses $appRoot).Count) { throw 'Ilova hali ishlayapti. Fayllar almashtirilmadi. Yopib qayta urining.' }
}
if ($Restore) {
    $last = Get-ChildItem -LiteralPath $backupRoot -Directory | Where-Object { $_.Name -like 'files-*' } | Sort-Object Name -Descending | Select-Object -First 1
    if (-not $last) { throw 'Ovoz fayllarining zaxirasi topilmadi' }
    foreach ($name in @('app.js','recordings.js')) { if (-not (Test-Path -LiteralPath (Join-Path $last.FullName $name))) { throw 'Zaxira toliq emas' } }
    foreach ($name in @('app.js','recordings.js')) { Copy-Item -LiteralPath (Join-Path $last.FullName $name) -Destination (Join-Path $webRoot $name) -Force }
    Write-Host 'Oldingi web fayllari tiklandi. S prefiksi bu amal bilan qaytarilmaydi.'
} else {
    $changed = @($manifest.files | Where-Object { (Get-FileHash -LiteralPath (Join-Path $webRoot $_.name) -Algorithm SHA256).Hash -ne $_.sha256 })
    if ($changed.Count) {
        $backup = Join-Path $backupRoot ('files-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
        $null = New-Item -ItemType Directory -Path $backup -Force
        foreach ($name in @('app.js','recordings.js')) { Copy-Item -LiteralPath (Join-Path $webRoot $name) -Destination (Join-Path $backup $name) }
        try {
            foreach ($entry in $manifest.files) {
                $destination = Join-Path $webRoot $entry.name
                $temporary = $destination + '.audio-patch-new'
                Copy-Item -LiteralPath (Join-Path (Join-Path $patchRoot 'web') $entry.name) -Destination $temporary -Force
                $replaceBackup = $destination + '.audio-patch-old'
                [IO.File]::Replace($temporary,$destination,$replaceBackup)
                Remove-Item -LiteralPath $replaceBackup -Force
                if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $entry.sha256) { throw 'Kochirilgan fayl tekshirilmadi' }
            }
        } catch {
            foreach ($name in @('app.js','recordings.js')) { Copy-Item -LiteralPath (Join-Path $backup $name) -Destination (Join-Path $webRoot $name) -Force }
            throw
        }
        Write-Host "Web fayllar yangilandi. Zaxira: $backup" -ForegroundColor Green
    } else { Write-Host 'Ovoz patchi allaqachon ornatilgan.' -ForegroundColor Green }
    Write-Host 'EXE, printer, LED, queue.db va yuklangan ovoz fayllari almashtirilmadi.'
    Write-Host 'F10 -> Ovozlar -> S1-S500 va p1-p5 ni birga tanlang -> Tanlangan ovozlarni biriktirish. Song TV ilovasini qayta oching.'
}
if (-not $NoStart -and (Test-Path -LiteralPath $exe)) { Start-Process -FilePath $exe }
