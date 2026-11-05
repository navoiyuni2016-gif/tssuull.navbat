param([Parameter(Mandatory=$true)][string]$TicketFile)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$t=Get-Content -LiteralPath $TicketFile -Raw -Encoding UTF8 | ConvertFrom-Json
$doc=New-Object System.Drawing.Printing.PrintDocument
$doc.PrinterSettings.PrinterName=$t.printer
if (!$doc.PrinterSettings.IsValid) { throw 'Printer topilmadi' }
$doc.PrintController=New-Object System.Drawing.Printing.StandardPrintController
$width=[int]([double]$t.width/25.4*100)
$doc.DefaultPageSettings.PaperSize=New-Object System.Drawing.Printing.PaperSize('Navbat',$width,650)
$doc.DefaultPageSettings.Margins=New-Object System.Drawing.Printing.Margins(12,12,12,12)
$handler=[System.Drawing.Printing.PrintPageEventHandler]{param($sender,$event)
  $normal=New-Object System.Drawing.Font('Arial',10)
  $large=New-Object System.Drawing.Font('Arial',36,[System.Drawing.FontStyle]::Bold)
  try {
    $y=[single]12;$w=[single]($event.PageBounds.Width-24)
    foreach($line in @($t.university,$t.service)) {
      $size=$event.Graphics.MeasureString($line,$normal,[int]$w)
      $event.Graphics.DrawString($line,$normal,[System.Drawing.Brushes]::Black,(New-Object System.Drawing.RectangleF(12,$y,$w,($size.Height+6))))
      $y+=$size.Height+10
    }
    $event.Graphics.DrawString([string]$t.label,$large,[System.Drawing.Brushes]::Black,[single]12,$y);$y+=65
    $event.Graphics.DrawString([string]$t.created,$normal,[System.Drawing.Brushes]::Black,[single]12,$y);$y+=30
    $event.Graphics.DrawString(([string]$t.ahead_label+': '+$t.ahead),$normal,[System.Drawing.Brushes]::Black,[single]12,$y)
    $event.HasMorePages=$false
  } finally {$normal.Dispose();$large.Dispose()}
}
$doc.add_PrintPage($handler)
try {$doc.Print()} finally {$doc.Dispose()}
