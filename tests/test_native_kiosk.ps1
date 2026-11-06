$ErrorActionPreference='Stop'
$source=Join-Path $PSScriptRoot '../windows/kiosk.ps1'
$directory=Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
$null=New-Item -ItemType Directory -Path (Join-Path $directory 'windows') -Force
try {
 Copy-Item -LiteralPath $source -Destination (Join-Path $directory 'windows/kiosk.ps1')
 [IO.File]::WriteAllText((Join-Path $directory 'TOShDOTAU.exe'),'fixture - never executed')
 $global:nativeKioskTestLaunches=@()
 function Start-Process { param($FilePath,$ArgumentList) $global:nativeKioskTestLaunches+=@{path=$FilePath;arguments=$ArgumentList} }
 & (Join-Path $directory 'windows/kiosk.ps1') -Mode Terminal
 if($global:nativeKioskTestLaunches.Count -ne 1){throw 'Terminal did not start exactly one EXE'}
 if($global:nativeKioskTestLaunches[0].path -ne (Join-Path $directory 'TOShDOTAU.exe')){throw 'External browser or wrong EXE launched'}
 if($global:nativeKioskTestLaunches[0].arguments -ne '--kiosk'){throw 'Kiosk argument missing'}
 foreach($path in @($source,(Join-Path $PSScriptRoot '../patches/native-startup/Enable-NativeStartup.ps1'))){
  $tokens=$null;$errors=$null;$null=[Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
  if($errors.Count){throw ($errors|Out-String)}
 }
 Write-Output 'PASS terminal launches native EXE once, does not enter browser loop; startup scripts parse'
}finally{Remove-Variable nativeKioskTestLaunches -Scope Global -ErrorAction SilentlyContinue;Remove-Item -LiteralPath $directory -Recurse -Force}
