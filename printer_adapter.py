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
    def __init__(self, connect, data, root, sender=None):
        self.connect=connect;self.data=Path(data);self.root=Path(root);self.stop=threading.Event();self.thread=None
        self.sender=sender or self.send_windows
    def start(self):
        with self.connect() as c:
            for table in ('print_jobs','printer_tests'):
                c.execute("UPDATE "+table+" SET status='uncertain',error='Server bosma paytida to‘xtagan. Qog‘ozni tekshiring; avtomatik takrorlanmadi.' WHERE status IN ('printing','dispatching')")
        self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start()
    def close(self):
        self.stop.set()
        if self.thread:self.thread.join()
    def run(self):
        while not self.stop.is_set():
            try:self.once()
            except Exception:
                import logging
                logging.getLogger('navbat').exception('Bosma xizmati xatosi')
            self.stop.wait(.5)
    def once(self):
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute("SELECT print_jobs.id AS job,tickets.*,services.name AS service_name,services.name_ru AS service_name_ru,services.name_en AS service_name_en FROM print_jobs JOIN tickets ON tickets.id=print_jobs.ticket JOIN services ON services.id=tickets.service WHERE print_jobs.status='pending' ORDER BY print_jobs.id LIMIT 1").fetchone()
            table='print_jobs'
            if not row:
                row=c.execute("SELECT id AS job,created FROM printer_tests WHERE status='pending' ORDER BY id LIMIT 1").fetchone();table='printer_tests'
            if not row:return
            config=management.settings(c)
            c.execute("UPDATE "+table+" SET status='printing' WHERE id=?",(row['job'],))
        result='printed';error=None
        try:
            if config['printer_mode']!='windows':raise ValueError('Windows printer rejimini tanlang.')
            diagnostic=table=='printer_tests'
            payload=dict(university=alphabet.text(config['university']),service='Printer diagnostikasi — sinov çeki' if diagnostic else alphabet.text(service_name(row)) if row['lang']=='uz' else service_name(row),label='TEST' if diagnostic else row['label'],created=dt.datetime.fromisoformat(row['created']).astimezone(dt.timezone(dt.timedelta(hours=5))).strftime('%d.%m.%Y %H:%M:%S'),ahead=0 if diagnostic else row['ahead'],ahead_label='Sinov' if diagnostic else {'uz':'Oldinda kutayotganlar','ru':'Перед вами в очереди','en':'People ahead'}[row['lang']],printer=config['printer_name'],width=config['paper_width_mm'],job=str(row['job']))
            self.sender(payload)
        except PrintUncertain as exc:result='uncertain';error=str(exc)
        except (ValueError,OSError) as exc:result='failed';error=str(exc)
        with self.connect() as c:c.execute('UPDATE '+table+' SET status=?,error=? WHERE id=?',(result,error,row['job']))
    def send_windows(self,payload):
        if os.name!='nt':raise ValueError('Windows printer rejimi faqat Windows’da ishlaydi')
        self.data.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w',suffix='.json',dir=self.data,encoding='utf-8',delete=False) as stream:
            json.dump(payload,stream,ensure_ascii=False);path=Path(stream.name)
        try:
            try:
                completed=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-File',str(self.root/'windows'/'print-ticket.ps1'),'-TicketFile',str(path)],capture_output=True,timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            except subprocess.TimeoutExpired:raise PrintUncertain('Bosma vaqti tugadi. Qog‘ozni tekshiring; avtomatik qayta chop etilmadi.')
            output=completed.stdout.decode('utf-8-sig',errors='replace').strip()
            try:answer=json.loads(output)
            except ValueError:answer={}
            if completed.returncode:
                detail=answer.get('error') or completed.stderr.decode('utf-8-sig',errors='replace').strip() or output or 'Windows bosma xatosi'
                message=str(detail)[:2000]
                if answer.get('stage')=='submit' or not answer:raise PrintUncertain(message)
                raise ValueError(message)
            if answer.get('ok') is not True:raise PrintUncertain('Windows javobi tasdiqlanmadi. Qog‘ozni va diagnostikani tekshiring.')
        finally:path.unlink(missing_ok=True)


class PrintUncertain(ValueError):pass


def diagnostics(connect,root):
    with connect() as c:
        config=management.settings(c)
        jobs=[dict(row) for row in c.execute('SELECT print_jobs.*,tickets.label,tickets.request AS ticket_request FROM print_jobs JOIN tickets ON tickets.id=print_jobs.ticket ORDER BY print_jobs.id DESC LIMIT 20')]
        tests=[dict(row) for row in c.execute('SELECT * FROM printer_tests ORDER BY id DESC LIMIT 5')]
    result=dict(settings={k:config[k] for k in ('printer_mode','printer_name','paper_width_mm')},jobs=jobs,tests=tests,platform=os.name,printers=[],physical_test_verified=False)
    if os.name!='nt':result['error']='Printer diagnostikasi Windows’da bajariladi.';return result
    try:
        completed=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-File',str(Path(root)/'windows'/'printer-info.ps1')],capture_output=True,timeout=20,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        result.update(json.loads(completed.stdout.decode('utf-8-sig')))
    except (OSError,ValueError,subprocess.SubprocessError) as exc:result['error']='Windows printerlarini o‘qib bo‘lmadi: '+str(exc)
    return result


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
            if c.execute("SELECT 1 FROM desktop_preferences WHERE key='printer_preset_v1'").fetchone() or management.settings(c)['printer_mode'] != 'html':
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
    """Apply the user's initial preset once; subsequent manual settings persist."""
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        if c.execute("SELECT 1 FROM desktop_preferences WHERE key='printer_preset_v1'").fetchone():return
        management.save_settings(c,dict(printer_mode='windows',printer_name=KIOSK_PRINTER,paper_width_mm=80))
        c.execute("INSERT INTO desktop_preferences VALUES ('printer_preset_v1','1')")
