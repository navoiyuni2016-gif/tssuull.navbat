"""Windows desktop entry point. Frozen with Python/Tk and all offline resources."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
import webbrowser
from desktop_runtime import data_directory,has_admin,instance_id,launch_command,validate_password

BASE='http://127.0.0.1:8080'


def matching_server(directory):
    try:
        # Local control must not pass through an inherited organization HTTP proxy.
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(BASE+'/api/health',timeout=1) as response:body=json.load(response)
        return body.get('app')=='toshdotau-navbat' and body.get('instance')==instance_id(directory)
    except (OSError,ValueError):return False


def ensure_server(directory):
    if matching_server(directory):return
    directory.mkdir(parents=True,exist_ok=True)
    environment=dict(os.environ,NAVBAT_DATA=str(directory))
    with (directory/'desktop-server.log').open('ab') as log:
        process=subprocess.Popen(launch_command('--server'),env=environment,stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    for _ in range(80):
        if matching_server(directory):return
        if process.poll() is not None:break
        time.sleep(.25)
    # Do not kill a possibly printing process or attach to a different installation.
    raise RuntimeError('Server oçilmadi. Eski app.py/server oynasini yoping va qayta sinang. Tafsilot: '+str(directory/'desktop-server.log'))


def open_terminal(directory):
    for base in [os.environ.get('ProgramFiles(x86)'),os.environ.get('ProgramFiles')]:
        if not base:continue
        edge=Path(base)/'Microsoft'/'Edge'/'Application'/'msedge.exe'
        if edge.is_file():
            subprocess.Popen([str(edge),'--kiosk',BASE+'/','--edge-kiosk-type=fullscreen','--no-first-run','--user-data-dir='+str(directory.parent/'edge-kiosk')])
            return
    webbrowser.open(BASE+'/')


def gui():
    import tkinter as tk
    from tkinter import ttk,messagebox,filedialog
    directory=data_directory()
    root=tk.Tk();root.title('TOŞDÖTAU — elektron navbat');root.geometry('620x510');root.minsize(580,470)
    root.configure(bg='#102d54')
    tk.Label(root,text='TOŞDÖTAU',font=('Segoe UI',25,'bold'),bg='#102d54',fg='white').pack(pady=(24,4))
    tk.Label(root,text='Elektron navbat tizimi',font=('Segoe UI',13),bg='#102d54',fg='#d5e7fa').pack()
    frame=ttk.Frame(root,padding=24);frame.pack(fill='both',expand=True,padx=24,pady=24)
    def error(exc):messagebox.showerror('TOŞDÖTAU',str(exc),parent=root)
    def start():
        try:ensure_server(directory)
        except Exception as exc:error(exc);return
        for child in frame.winfo_children():child.destroy()
        ttk.Label(frame,text='Server işlayapti. Terminal foydalanishga tayyor.',wraplength=490,font=('Segoe UI',12,'bold')).pack(pady=(0,12))
        def terminal():open_terminal(directory);root.iconify()
        for text,command in [('Terminalni töliq ekranda oçiş',terminal),('Administrator paneli',lambda:webbrowser.open(BASE+'/admin')),('Xodim paneli',lambda:webbrowser.open(BASE+'/staff')),('TV ekranini sinaş',lambda:webbrowser.open(BASE+'/tv?autostart=1'))]:
            ttk.Button(frame,text=text,command=command).pack(fill='x',pady=4)
        def printer():
            import printer_adapter
            import app
            dialog=tk.Toplevel(root);dialog.title('Printer');dialog.geometry('450x180');dialog.transient(root)
            try:names=printer_adapter.installed_printers()
            except Exception as exc:dialog.destroy();error(exc);return
            ttk.Label(dialog,text='Windows printerini tanlang (80 mm):').pack(pady=12)
            choice=ttk.Combobox(dialog,values=names,state='readonly',width=42);choice.pack()
            if names:choice.set(printer_adapter.KIOSK_PRINTER if printer_adapter.KIOSK_PRINTER in names else names[0])
            def save():
                try:printer_adapter.configure_printer(app.connect,choice.get())
                except Exception as exc:error(exc);return
                dialog.destroy();messagebox.showinfo('Printer','Avtomatik çek çiqariş sozlandi.',parent=root)
            ttk.Button(dialog,text='Saqlaş',command=save).pack(pady=12)
        ttk.Button(frame,text='Printerni sozlaş',command=printer).pack(fill='x',pady=4)
        ttk.Label(frame,text='Login: admin · Server ilova yopilganda ham fonda işlaydi.\nMaʼlumotlar: '+str(directory),wraplength=490).pack(pady=10)
        root.after(250,terminal)
    def ready():
        if has_admin(directory):start();return
        for child in frame.winfo_children():child.destroy()
        ttk.Label(frame,text='Birinçi oçiliş: administrator parolini yarating.',font=('Segoe UI',11,'bold')).pack(pady=(0,14))
        ttk.Label(frame,text='Parol — kamida 12 belgi').pack(anchor='w');first=ttk.Entry(frame,show='*');first.pack(fill='x',pady=(4,10))
        ttk.Label(frame,text='Parolni qayta kiriting').pack(anchor='w');second=ttk.Entry(frame,show='*');second.pack(fill='x',pady=(4,12))
        def create():
            try:
                validate_password(first.get(),second.get())
                import app
                app.initialize(first.get())
            except Exception as exc:error(exc);return
            first.delete(0,'end');second.delete(0,'end');start()
        ttk.Button(frame,text='Parolni saqlaş va terminalni oçiş',command=create).pack(fill='x',pady=5)
        def restore():
            source=filedialog.askdirectory(title='Eski loyihadagi data papkasini tanlang',parent=root)
            if not source:return
            try:
                if directory.exists():
                    raise ValueError('Yangi data papkasi allaqaçon mavjud. Uni ustidan yozilmadi. Zaxira/tiklaş yöriğidan foydalaning.')
                from tools.prepare_install_data import copy_data
                copy_data(source,directory)
            except Exception as exc:error(exc);return
            ready()
        ttk.Button(frame,text='Eski data papkasidan bazani köçiriş',command=restore).pack(fill='x',pady=5)
        first.focus_set()
    ready();root.mainloop()


def self_test(destination):
    """Exercise the actual frozen Python/Tk/resources without touching user data."""
    result={}
    try:
        with tempfile.TemporaryDirectory() as folder:
            os.environ['NAVBAT_DATA']=folder
            import app,report_exports
            app.DATA=Path(folder);app.initialize('frozen-self-test-password-123')
            ticket=app.issue(1,'frozen-self-test-request-123')
            assert ticket['label']=='A001'
            for name in ['web/index.html','web/assets/university-logo.png','web/assets/campus-background.png','fonts/DejaVuSans.ttf','windows/print-ticket.ps1']:
                assert (app.ROOT/name).is_file(),name
            with app.connect() as c:
                data=report_exports.snapshot(c,ticket['day'],ticket['day'])
                for fmt in ('xlsx','docx','pdf'):assert len(report_exports.render(data,fmt)[0])>1000
            import tkinter as tk
            window=tk.Tk();window.withdraw();window.update();window.destroy()
            result={'ok':True,'frozen':bool(getattr(sys,'frozen',False)),'ticket':ticket['label']}
    except Exception:
        import traceback
        result={'ok':False,'error':traceback.format_exc()}
    Path(destination).write_text(json.dumps(result),encoding='utf-8')
    return 0 if result.get('ok') else 1


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--server',action='store_true');parser.add_argument('--kiosk',action='store_true');parser.add_argument('--self-test')
    args=parser.parse_args()
    if args.self_test:raise SystemExit(self_test(args.self_test))
    os.environ['NAVBAT_DATA']=str(data_directory())
    import app
    if args.server:
        app.initialize();app.run_server('0.0.0.0',8080)
    else:gui()

if __name__=='__main__':main()
