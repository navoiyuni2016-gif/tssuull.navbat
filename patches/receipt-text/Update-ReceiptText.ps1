[CmdletBinding()]
param([string]$AppPath='', [string]$Server='http://127.0.0.1:8080', [switch]$NoStart, [switch]$Restore)
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


$root=(Resolve-Path -LiteralPath $AppPath).ProviderPath
$resourceRoot=Join-Path $root '_internal'
if (-not (Test-Path -LiteralPath (Join-Path $resourceRoot 'web/app.js'))) { $resourceRoot=$root }
$uri=[Uri]$Server
if ($uri.Scheme -ne 'http' -or $uri.Host -notin @('127.0.0.1','localhost') -or $uri.UserInfo -or $uri.AbsolutePath -ne '/') { throw 'Faqat infokiosk localhost manzili ishlatiladi' }
$serverBase=$uri.GetLeftPart([UriPartial]::Authority)
$backupRoot=Join-Path $root 'receipt-text-backups'
$targets=@('web/app.js','windows/print-ticket.ps1','windows/university-names.json')
foreach($name in $targets[0..1]) { if(-not(Test-Path -LiteralPath (Join-Path $resourceRoot $name))){throw "Ilova fayli topilmadi: $name"} }
if (-not $Restore) {
  $manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw|ConvertFrom-Json
  if(@($manifest.files).Count -ne 2){throw 'Manifest notogri'}
  foreach($entry in $manifest.files){
    if($entry.path -notin $targets[0..1]){throw 'Manifest fayl nomi notogri'}
    if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $entry.path) -Algorithm SHA256).Hash -ne $entry.sha256){throw 'Patch SHA256 mos emas'}
  }
  try {$state=Invoke-RestMethod "$serverBase/api/state" -TimeoutSec 5} catch {throw 'Navbat ilovasini avval oching. Universitet nomi serverdan oqilishi kerak.'}
  if(-not $state.university){throw 'Universitet nomi serverda topilmadi'}
  $names=@{uz=[string]$state.university;ru='Ташкентский государственный университет узбекского языка и литературы имени Алишера Навои';en="Alisher Navo'i Tashkent State University of Uzbek Language and Literature"}
  $namesPath=Join-Path $resourceRoot 'windows/university-names.json'
  if(Test-Path -LiteralPath $namesPath){$saved=Get-Content -LiteralPath $namesPath -Raw -Encoding UTF8|ConvertFrom-Json;foreach($lang in @('ru','en')){if($saved.$lang){$names[$lang]=[string]$saved.$lang}}}
  foreach($lang in @('uz','ru','en')){if($state.university_names.$lang){$names[$lang]=[string]$state.university_names.$lang}}
}
function Get-AppProcesses {
  @(Get-Process -Name TOShDOTAU -ErrorAction SilentlyContinue|Where-Object {try{(Split-Path -Parent $_.Path) -eq $root}catch{$false}})
}
if(@(Get-AppProcesses).Count){
  Write-Host 'Navbat ilovasini odatdagidek administrator paroli bilan yoping. Jarayon majburan toxtatilmaydi.' -ForegroundColor Yellow
  $null=Read-Host 'Yopilgach Enter bosing'
  if(@(Get-AppProcesses).Count){throw 'Ilova hali ochiq. Yopib qayta urining.'}
}
if($Restore){
  $last=Get-ChildItem -LiteralPath $backupRoot -Directory|Sort-Object Name -Descending|Select-Object -First 1
  if(-not $last){throw 'Zaxira topilmadi'}
  foreach($name in $targets){$saved=Join-Path $last.FullName $name;$target=Join-Path $resourceRoot $name;if(Test-Path -LiteralPath $saved){Copy-Item -LiteralPath $saved -Destination $target -Force}elseif($name -eq 'windows/university-names.json' -and (Test-Path -LiteralPath $target)){Remove-Item -LiteralPath $target}}
  Write-Host 'Oldingi chek va interfeys fayllari tiklandi.'
}else{
  $backup=Join-Path $backupRoot (Get-Date -Format 'yyyyMMdd-HHmmss-fff')
  foreach($name in $targets){
    $saved=Join-Path $backup $name;$null=New-Item -ItemType Directory -Path (Split-Path -Parent $saved) -Force
    $target=Join-Path $resourceRoot $name;if(Test-Path -LiteralPath $target){Copy-Item -LiteralPath $target -Destination $saved}
  }
  try{
    $js=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'web/app.js') -Raw -Encoding UTF8
    $translations=@{ru=$names.ru;en=$names.en}|ConvertTo-Json -Compress
    $pattern='(?m)^const universityTranslations=.*?;\r?$'
    if([regex]::Matches($js,$pattern).Count -ne 1){throw 'Tarjima belgisi topilmadi'}
    $js=[regex]::Replace($js,$pattern,[Text.RegularExpressions.MatchEvaluator]{param($m) 'const universityTranslations='+$translations+';'})
    $content=@{'web/app.js'=$js;'windows/print-ticket.ps1'=(Get-Content -LiteralPath (Join-Path $PSScriptRoot 'windows/print-ticket.ps1') -Raw -Encoding UTF8);'windows/university-names.json'=($names|ConvertTo-Json)}
    foreach($name in $targets){
      $target=Join-Path $resourceRoot $name;$temporary=$target+'.receipt-text-new'
      [IO.File]::WriteAllText($temporary,[string]$content[$name],(New-Object Text.UTF8Encoding($true)))
      if(Test-Path -LiteralPath $target){$old=$target+'.receipt-text-old';[IO.File]::Replace($temporary,$target,$old);Remove-Item -LiteralPath $old -Force}else{[IO.File]::Move($temporary,$target)}
    }
  }catch{
    foreach($name in $targets){$saved=Join-Path $backup $name;$target=Join-Path $resourceRoot $name;if(Test-Path -LiteralPath $saved){Copy-Item -LiteralPath $saved -Destination $target -Force}elseif($name -eq 'windows/university-names.json' -and (Test-Path -LiteralPath $target)){Remove-Item -LiteralPath $target}}
    throw
  }
  Write-Host 'Chek satrlari va UZ/RU/EN nomlari yangilandi. Baza, ovozlar, printer sozlamalari saqlandi.' -ForegroundColor Green
  Write-Host "Zaxira: $backup"
  Write-Host 'Bitta yangi chek chiqaring. data/print-diagnostics/last-input.json va last-layout.json sababni korsatadi.'
}
$exe=Join-Path $root 'TOShDOTAU.exe'
if(-not $NoStart -and (Test-Path -LiteralPath $exe)){Start-Process -FilePath $exe}
