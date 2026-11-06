param([Parameter(Mandatory=$true)][string]$TicketFile,[switch]$InspectOnly)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.Encoding]::UTF8
$phase='validate';$doc=$null
function Get-ReceiptBounds {
  param([double]$PageWidth,[double]$PageHeight,[double]$PrintableLeft,[double]$PrintableTop,[double]$PrintableWidth,[double]$PrintableHeight,[double]$HardMarginX,[double]$HardMarginY)
  # Printer coordinates start at the hardware margin. Keep all ink inside
  # both the requested paper and the driver's actual printable rectangle.
  $left=[Math]::Max(12,[Math]::Max($PrintableLeft,$HardMarginX)+4)
  $top=[Math]::Max(12,[Math]::Max($PrintableTop,$HardMarginY)+4)
  $right=[Math]::Min($PageWidth-12,$PrintableLeft+$PrintableWidth-4)
  $bottom=[Math]::Min($PageHeight-12,$PrintableTop+$PrintableHeight-4)
  if($right-$left -lt 40 -or $bottom-$top -lt 40){throw 'Printer bosma maydoni juda kichik. Windows qogoz olchamini tekshiring.'}
  @{X=[single]($left-$HardMarginX);Y=[single]($top-$HardMarginY);Width=[single]($right-$left);Height=[single]($bottom-$top)}
}
function Split-ReceiptLines {
  param([string]$Text,[double]$Width,[scriptblock]$Measure)
  $lines=New-Object 'Collections.Generic.List[string]'
  $current=''
  foreach($word in @($Text -split '\s+' | Where-Object { $_ })) {
    $candidate=if($current){$current+' '+$word}else{$word}
    if ((& $Measure $candidate) -le $Width) { $current=$candidate;continue }
    if ($current) { $lines.Add($current);$current='' }
    # Split an unusually long word by Unicode text element, never discard a glyph.
    $elements=[Globalization.StringInfo]::GetTextElementEnumerator($word)
    while($elements.MoveNext()) {
      $glyph=[string]$elements.Current
      if ((& $Measure $glyph) -gt $Width) { throw 'Bitta belgi bosma maydoniga sigmadi' }
      if ($current -and (& $Measure ($current+$glyph)) -gt $Width) { $lines.Add($current);$current='' }
      $current+=$glyph
    }
  }
  if($current){$lines.Add($current)}
  if(($lines.ToArray() -join '' -replace '\s','') -cne ($Text -replace '\s','')) { throw 'Bosma satrlarida belgi yoqoldi' }
  $lines.ToArray()
}
function Write-ReceiptTrace([string]$Name,$Value) {
  $directory=Join-Path (Split-Path -Parent $TicketFile) 'print-diagnostics'
  $null=[IO.Directory]::CreateDirectory($directory)
  [IO.File]::WriteAllText((Join-Path $directory $Name),($Value|ConvertTo-Json -Depth 10),(New-Object Text.UTF8Encoding($false)))
}
function Draw-ReceiptText {
  param($Graphics,$Font,$Format,[string]$Text,[single]$X,[single]$Width,[ref]$Y,$Trace)
  $available=[single]($Width-8)
  $measure={param($value) $Graphics.MeasureString([string]$value,$Font,(New-Object Drawing.SizeF(10000,10000)),$Format).Width}
  $lines=@(Split-ReceiptLines -Text $Text -Width $available -Measure $measure)
  $Trace.Add(@{text=$Text;lines=$lines;width=$available})
  foreach($line in $lines) {
    $size=$Graphics.MeasureString([string]$line,$Font,(New-Object Drawing.SizeF(10000,10000)),$Format)
    $height=[single]($size.Height+4)
    $Graphics.DrawString([string]$line,$Font,[Drawing.Brushes]::Black,(New-Object Drawing.RectangleF(($X+4),$Y.Value,$available,$height)),$Format)
    $Y.Value=[single]($Y.Value+$height)
  }
  $Y.Value=[single]($Y.Value+8)
}

function Invoke-ReceiptPrint {
try {
  Add-Type -AssemblyName System.Drawing
  if((Get-Service Spooler).Status -ne 'Running'){throw 'Windows Print Spooler ishlamayapti'}
  $doc=New-Object Drawing.Printing.PrintDocument
  $doc.PrinterSettings.PrinterName=[string]$t.printer
  if(!$doc.PrinterSettings.IsValid){throw ('Printer ushbu Windows hisobiga korinmadi: '+$t.printer+' | '+[Security.Principal.WindowsIdentity]::GetCurrent().Name)}
  $device=Get-CimInstance Win32_Printer -ErrorAction SilentlyContinue | Where-Object {$_.Name -eq $t.printer} | Select-Object -First 1
  if($device.WorkOffline -or $device.PrinterStatus -eq 7 -or $device.DetectedErrorState -in @(4,7,8,9,11)){throw 'Printer Windowsda offline. USB, qogoz va printer navbatini tekshiring.'}
  $doc.DocumentName='TOShDOTAU-'+[string]$t.document_key
  $existing=Get-CimInstance Win32_PrintJob -ErrorAction SilentlyContinue | Where-Object {$_.Document -eq $doc.DocumentName}
  if($existing){throw 'Shu chek Windows navbatida allaqachon mavjud. Kuting yoki eski vazifani Windows navbatidan tekshirib olib tashlang.'}
  $doc.PrintController=New-Object Drawing.Printing.StandardPrintController
  $width=[int]([double]$t.width/25.4*100)
  $doc.DefaultPageSettings.PaperSize=New-Object Drawing.Printing.PaperSize('Navbat',$width,550)
  $doc.DefaultPageSettings.Margins=New-Object Drawing.Printing.Margins(12,12,12,12)
  $handler=[Drawing.Printing.PrintPageEventHandler]{param($sender,$event)
    $normal=New-Object Drawing.Font('Arial',10)
    $large=New-Object Drawing.Font('Arial',36,[Drawing.FontStyle]::Bold)
    $format=[Drawing.StringFormat]::GenericTypographic.Clone();$format.Alignment=[Drawing.StringAlignment]::Center;$format.FormatFlags=$format.FormatFlags -bor [Drawing.StringFormatFlags]::NoWrap;$format.Trimming=[Drawing.StringTrimming]::None
    try {
      $event.Graphics.PageUnit=[Drawing.GraphicsUnit]::Display
      $area=$event.PageSettings.PrintableArea
      $bounds=Get-ReceiptBounds -PageWidth $event.PageBounds.Width -PageHeight $event.PageBounds.Height -PrintableLeft $area.Left -PrintableTop $area.Top -PrintableWidth $area.Width -PrintableHeight $area.Height -HardMarginX $event.PageSettings.HardMarginX -HardMarginY $event.PageSettings.HardMarginY
      $x=[single]$bounds.X;$y=[single]$bounds.Y;$w=[single]$bounds.Width
      $trace=New-Object 'Collections.Generic.List[object]'
      foreach($line in @($t.university,$t.service)) {
        Draw-ReceiptText $event.Graphics $normal $format ([string]$line) $x $w ([ref]$y) $trace
      }
      Draw-ReceiptText $event.Graphics $large $format ([string]$t.label) $x $w ([ref]$y) $trace
      foreach($line in @([string]$t.created,([string]$t.ahead_label+': '+$t.ahead))) {
        Draw-ReceiptText $event.Graphics $normal $format $line $x $w ([ref]$y) $trace
      }
      Write-ReceiptTrace 'last-layout.json' @{university=[string]$t.university;lang=$t.lang;bounds=$bounds;hard_margin_x=$event.PageSettings.HardMarginX;hard_margin_y=$event.PageSettings.HardMarginY;printable_area=@{x=$area.X;y=$area.Y;width=$area.Width;height=$area.Height};rows=$trace.ToArray()}
      if($y -gt $bounds.Y+$bounds.Height){throw 'Chek balandligi yetarli emas; matn kesilmasligi uchun bosma toxtatildi'}
      $event.HasMorePages=$false
    } finally {$normal.Dispose();$large.Dispose();$format.Dispose()}
  }
  $doc.add_PrintPage($handler)
  $phase='submit';$doc.Print()
  for($i=0;$i -lt 6;$i++){
    $queued=Get-CimInstance Win32_PrintJob -ErrorAction SilentlyContinue | Where-Object {$_.Document -eq $doc.DocumentName} | Select-Object -First 1
    if(!$queued){break}
    if(([int]$queued.StatusMask -band 1634) -ne 0){throw ('Windows bosma navbatida xato: '+$queued.Status+'. Qogoz va USBni tekshiring; eski vazifa navbatda qolgan bolishi mumkin.')}
    Start-Sleep -Milliseconds 200
  }
  @{ok=$true;stage='accepted';message='Windows print queue accepted the job. Physical paper output is not verified.'}|ConvertTo-Json -Compress
} catch {
  @{ok=$false;stage=$phase;error=$_.Exception.Message;type=$_.Exception.GetType().FullName;code=$_.Exception.HResult}|ConvertTo-Json -Compress
  exit 1
} finally {if($doc){$doc.Dispose()}}

}
try {
  $t=Get-Content -LiteralPath $TicketFile -Raw -Encoding UTF8 | ConvertFrom-Json
  $diagnosticDirectory=Join-Path (Split-Path -Parent $TicketFile) 'print-diagnostics'
  $null=[IO.Directory]::CreateDirectory($diagnosticDirectory)
  $inputHash=(Get-FileHash -LiteralPath $TicketFile -Algorithm SHA256).Hash
  [IO.File]::Copy($TicketFile,(Join-Path $diagnosticDirectory 'last-input.json'),$true)
  $inputUniversity=[string]$t.university
  $legacy=-not ($t.PSObject.Properties.Name -contains 'lang')
  $lang=if($legacy){switch([string]$t.ahead_label){'Перед вами в очереди'{'ru'} 'People ahead'{'en'} default{'uz'}}}else{[string]$t.lang}
  if($lang -notin @('uz','ru','en')){throw 'Chipta tili notogri'}
  $namesFile=Join-Path $PSScriptRoot 'university-names.json'
  if($legacy -and (Test-Path -LiteralPath $namesFile)) {
    $names=Get-Content -LiteralPath $namesFile -Raw -Encoding UTF8|ConvertFrom-Json
    if(-not $names.$lang){throw 'Universitet tarjimasi topilmadi'}
    $t.university=[string]$names.$lang
  }
  $t|Add-Member -NotePropertyName lang -NotePropertyValue $lang -Force
  Write-ReceiptTrace 'last-effective.json' $t
  # The legacy EXE omits lang; normalize its private job file before GDI reads it.
  [IO.File]::WriteAllText($TicketFile,($t|ConvertTo-Json -Depth 10),(New-Object Text.UTF8Encoding($false)))
  Write-ReceiptTrace 'last-text-check.json' @{input_sha256=$inputHash;input_university=$inputUniversity;effective_university=[string]$t.university;lang=$lang;legacy_payload=$legacy;input_characters=@($inputUniversity.ToCharArray()|ForEach-Object{@{character=[string]$_;codepoint=[int]$_}})}
  if($InspectOnly){@{ok=$true;stage='inspect';printed=$false}|ConvertTo-Json -Compress;exit 0}
  Invoke-ReceiptPrint
} catch {
  @{ok=$false;stage="validate";error=$_.Exception.Message}|ConvertTo-Json -Compress
  exit 1
}
