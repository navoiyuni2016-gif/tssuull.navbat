param([string]$BindAddress='0.0.0.0',[int]$Port=8080)
$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
py -3 app.py --host $BindAddress --port $Port
exit $LASTEXITCODE
