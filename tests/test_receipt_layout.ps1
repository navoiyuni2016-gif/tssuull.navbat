$ErrorActionPreference='Stop'
$path=Join-Path $PSScriptRoot '../windows/print-ticket.ps1'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
if ($errors.Count) { throw ($errors | Out-String) }
$function=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq 'Get-ReceiptBounds'},$true)
Invoke-Expression $function.Extent.Text
foreach($case in @(@(315,550,0,0,284,550,0,0),@(315,550,15,8,280,530,15,8),@(228,550,10,10,208,530,10,10),@(315,550,0,0,315,550,0,0))) {
  $b=Get-ReceiptBounds @case
  $physicalLeft=$b.X+$case[6];$physicalRight=$physicalLeft+$b.Width
  if ($physicalLeft -lt $case[2]+4 -or $physicalRight -gt $case[2]+$case[4]-4 -or $physicalRight -gt $case[0]-12 -or $b.X -lt 0) { throw 'Ink outside printable/paper bounds' }
}
$b=Get-ReceiptBounds 315 550 0 0 284 550 0 0
if ($b.Width -ne 268) { throw '80mm paper with narrower print head must wrap within 268 units' }
$rejected=$false
try { Get-ReceiptBounds 315 550 0 0 30 550 0 0 } catch { $rejected=$true }
if (-not $rejected) { throw 'Invalid driver area not rejected' }
Write-Output 'PASS receipt bounds: 80mm and 58mm, narrow head, hardware margins, invalid area, PowerShell parser'
