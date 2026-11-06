"""Durable local printer worker; no network listener or raw ESC/POS assumptions."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import management
import alphabet


def service_name(ticket):
    key={'ru':'service_name_ru','en':'service_name_en'}.get(ticket['lang'],'service_name')
    return ticket[key] or ticket['service_name']


def preview(ticket, service, university):
    escape=lambda v:html.escape(alphabet.text(str(v)) if ticket['lang']=='uz' else str(v))
    ahead_label={'uz':'Oldinda kutayotganlar','ru':'Перед вами в очереди','en':'People ahead'}[ticket['lang']]
    return ('<!doctype html><html lang="'+ticket['lang']+'"><meta charset="utf-8"><title>'+{'uz':'Çipta','ru':'Билет','en':'Ticket'}[ticket['lang']]+'</title>'
      '<style>@page{size:80mm auto;margin:4mm}body{font:14px Arial;text-align:center;width:72mm;margin:auto}.number{font-size:64px;font-weight:bold}button{margin:20px}@media print{button{display:none}}</style>'
      '<h3>'+escape(university)+'</h3><p>'+escape(service)+'</p><div class="number">'+escape(ticket['label'])+'</div><p>'+escape(ticket['created'])+'</p><p>'+escape(ahead_label)+': '+escape(ticket['ahead'])+'</p>')


class Worker:
    def __init__(self, connect, data, root):
        self.connect=connect;self.data=Path(data);self.root=Path(root);self.stop=threading.Event()
    def start(self):
        with self.connect() as c:
            c.execute("UPDATE print_jobs SET status='uncertain',error='Server bosma paytida to‘xtagan. Qog‘ozni tekshirib qayta chop eting.' WHERE status='dispatching'")
        threading.Thread(target=self.run,daemon=True).start()
    def run(self):
        while not self.stop.is_set():
            try:self.once()
            except Exception:
                # Do not lose the worker; status is persisted before external I/O.
                import logging
                logging.getLogger('navbat').exception('Bosma xizmati xatosi')
            self.stop.wait(1)
    def once(self):
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute("SELECT print_jobs.id AS job,tickets.*,services.name AS service_name,services.name_ru AS service_name_ru,services.name_en AS service_name_en FROM print_jobs JOIN tickets ON tickets.id=print_jobs.ticket JOIN services ON services.id=tickets.service WHERE print_jobs.status='pending' ORDER BY print_jobs.id LIMIT 1").fetchone()
            if not row:return
            config=management.settings(c)
            c.execute("UPDATE print_jobs SET status='dispatching' WHERE id=?",(row['job'],))
        result='sent';error=None
        try:
            if config['printer_mode']!='windows':raise ValueError('Printer rejimi o‘zgargan. Sinov ko‘rinishidan foydalaning.')
            if os.name!='nt':raise ValueError('Windows printer rejimi faqat Windows’da ishlaydi')
            payload=dict(university=alphabet.text(config['university']),service=alphabet.text(service_name(row)) if row['lang']=='uz' else service_name(row),label=row['label'],created=row['created'],ahead=row['ahead'],ahead_label={'uz':'Oldinda kutayotganlar','ru':'Перед вами в очереди','en':'People ahead'}[row['lang']],printer=config['printer_name'],width=config['paper_width_mm'])
            self.data.mkdir(parents=True,exist_ok=True)
            with tempfile.NamedTemporaryFile(mode='w',suffix='.json',dir=self.data,encoding='utf-8',delete=False) as stream:
                json.dump(payload,stream,ensure_ascii=False);path=Path(stream.name)
            try:
                completed=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-File',str(self.root/'windows'/'print-ticket.ps1'),'-TicketFile',str(path)],capture_output=True,timeout=45)
                if completed.returncode:raise ValueError('Windows bosma xatosi. Printer drayveri, nomi va qog‘ozini tekshiring.')
            finally:path.unlink(missing_ok=True)
        except subprocess.TimeoutExpired:
            result='uncertain';error='Bosma vaqti tugadi. Qog‘oz chiqqanini tekshiring; keyin shu chiptani qayta chop eting.'
        except (ValueError,OSError) as exc:result='failed';error=str(exc)
        with self.connect() as c:c.execute('UPDATE print_jobs SET status=?,error=? WHERE id=?',(result,error,row['job']))


KIOSK_PRINTER = 'KPOS_80 Printer(1)'


def installed_printers():
    """Read driver names from the same Windows account that will print."""
    if os.name != 'nt':
        return []
    command = "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; Add-Type -AssemblyName System.Drawing; @([System.Drawing.Printing.PrinterSettings]::InstalledPrinters) | ConvertTo-Json -Compress"
    result = subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',command],capture_output=True,timeout=15,check=True)
    value = json.loads(result.stdout.decode('utf-8-sig').strip() or '[]')
    return [value] if isinstance(value,str) else value or []


def configure_printer(connect, name=KIOSK_PRINTER, *, automatic=False):
    """Select only an installed driver; never send a test or replay old jobs."""
    if automatic:
        with connect() as c:
            if management.settings(c)['printer_mode'] != 'html':
                return False
    if name not in installed_printers():
        if automatic:
            return False
        raise ValueError('Printer topilmadi: '+name+'. Windows drayverini va printer nomini tekshiring.')
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        if automatic and management.settings(c)['printer_mode'] != 'html':
            return False
        management.save_settings(c,dict(printer_mode='windows',printer_name=name,paper_width_mm=80))
    return True


def apply_kiosk_preset(connect):
    """The dedicated Windows EXE always starts with the user's KPOS/80 mm preset.

    Store the selection even if the printer is temporarily offline. The durable
    worker reports driver/printing failures; it never opens a browser PDF dialog
    and never replays old preview jobs when these settings change.
    """
    with connect() as c:
        management.save_settings(c,dict(printer_mode='windows',printer_name=KIOSK_PRINTER,paper_width_mm=80))
