param([Parameter(Mandatory=$true)][string]$TicketFile)
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
try {
  Add-Type -AssemblyName System.Drawing
  $t=Get-Content -LiteralPath $TicketFile -Raw -Encoding UTF8 | ConvertFrom-Json
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
    $format=New-Object Drawing.StringFormat;$format.Alignment=[Drawing.StringAlignment]::Center
    try {
      $event.Graphics.PageUnit=[Drawing.GraphicsUnit]::Display
      $area=$event.PageSettings.PrintableArea
      $bounds=Get-ReceiptBounds -PageWidth $event.PageBounds.Width -PageHeight $event.PageBounds.Height -PrintableLeft $area.Left -PrintableTop $area.Top -PrintableWidth $area.Width -PrintableHeight $area.Height -HardMarginX $event.PageSettings.HardMarginX -HardMarginY $event.PageSettings.HardMarginY
      $x=[single]$bounds.X;$y=[single]$bounds.Y;$w=[single]$bounds.Width
      $layout=New-Object Drawing.SizeF($w,10000)
      foreach($line in @($t.university,$t.service)) {
        $size=$event.Graphics.MeasureString([string]$line,$normal,$layout,$format)
        $event.Graphics.DrawString([string]$line,$normal,[Drawing.Brushes]::Black,(New-Object Drawing.RectangleF($x,$y,$w,($size.Height+6))),$format)
        $y+=$size.Height+10
      }
      $event.Graphics.DrawString([string]$t.label,$large,[Drawing.Brushes]::Black,(New-Object Drawing.RectangleF($x,$y,$w,65)),$format);$y+=70
      foreach($line in @([string]$t.created,([string]$t.ahead_label+': '+$t.ahead))) {
        $size=$event.Graphics.MeasureString($line,$normal,$layout,$format)
        $event.Graphics.DrawString($line,$normal,[Drawing.Brushes]::Black,(New-Object Drawing.RectangleF($x,$y,$w,($size.Height+6))),$format);$y+=$size.Height+8
      }
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
