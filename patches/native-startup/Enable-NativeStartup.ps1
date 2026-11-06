[CmdletBinding()]
param([string]$AppPath='')
$ErrorActionPreference='Stop'
if(-not $AppPath){
 $running=@(Get-Process -Name TOShDOTAU -ErrorAction SilentlyContinue|ForEach-Object {try{Split-Path -Parent $_.Path}catch{}}|Select-Object -Unique)
 if($running.Count -eq 1){$AppPath=$running[0]}
 elseif($running.Count -eq 0 -and $env:LOCALAPPDATA){$candidate=Join-Path $env:LOCALAPPDATA 'Programs/TOShDOTAU';if(Test-Path -LiteralPath (Join-Path $candidate 'TOShDOTAU.exe')){$AppPath=$candidate}}
 if(-not $AppPath){$AppPath=Read-Host 'TOShDOTAU.exe turgan papka yolini kiriting'}
}
$root=(Resolve-Path -LiteralPath $AppPath).ProviderPath
$exe=Join-Path $root 'TOShDOTAU.exe'
if(-not(Test-Path -LiteralPath $exe -PathType Leaf)){throw 'TOShDOTAU.exe topilmadi; hech narsa ozgarmadi'}
$backup=Join-Path $env:LOCALAPPDATA ('TOShDOTAU/startup-backups/'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$null=New-Item -ItemType Directory -Path $backup -Force
$tasks=@()
foreach($name in @('UniversitetNavbatKiosk','UniversitetNavbatDisplayTerminal')){
 $task=Get-ScheduledTask -TaskName $name -TaskPath '\' -ErrorAction SilentlyContinue
 if($task){
  Export-ScheduledTask -TaskName $name -TaskPath '\'|Set-Content -LiteralPath (Join-Path $backup ($name+'.xml')) -Encoding UTF8
  $tasks+=@{Name=$name;Enabled=[bool]$task.Settings.Enabled}
 }
}
$startup=[Environment]::GetFolderPath('Startup')
if(-not $startup){throw 'Joriy Windows foydalanuvchi Startup papkasi topilmadi'}
$link=Join-Path $startup 'TOShDOTAU.lnk'
if(Test-Path -LiteralPath $link){Copy-Item -LiteralPath $link -Destination (Join-Path $backup 'TOShDOTAU.lnk')}
try{
 foreach($task in $tasks){Disable-ScheduledTask -TaskName $task.Name -TaskPath '\'|Out-Null;Write-Host ('Eski terminal vazifasi ochirildi: '+$task.Name)}
 $shell=New-Object -ComObject WScript.Shell
 $shortcut=$shell.CreateShortcut($link);$shortcut.TargetPath=$exe;$shortcut.Arguments='--kiosk';$shortcut.WorkingDirectory=$root;$shortcut.Description='TOShDOTAU native terminal';$shortcut.Save()
} catch {
 foreach($task in $tasks){if($task.Enabled){Enable-ScheduledTask -TaskName $task.Name -TaskPath '\' -ErrorAction SilentlyContinue|Out-Null}}
 if(Test-Path -LiteralPath (Join-Path $backup 'TOShDOTAU.lnk')){Copy-Item -LiteralPath (Join-Path $backup 'TOShDOTAU.lnk') -Destination $link -Force}
 throw
}
Write-Host 'TAYYOR: Windows hisobiga kirganda tashqi brauzer emas, TOShDOTAU.exe ochiladi.' -ForegroundColor Green
Write-Host "EXE: $exe"
Write-Host "Zaxira: $backup"
Write-Host 'Hozirgi brauzerni yoping. Kompyuterni odatdagidek qayta yoqing. Dastur va baza fayllari ozgarmadi.'
$service=Get-Service -Name UniversitetNavbat -ErrorAction SilentlyContinue
if($service){Write-Warning ('Eski UniversitetNavbat server xizmati bor: '+$service.Status+'. U ozgartirilmadi. EXE 8080 port band desa, ushbu xabarni yuboring; bazani tekshirmasdan xizmatni ochirmang.')}
