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
from desktop_runtime import data_directory,has_admin,instance_id,launch_command,validate_password

BASE='http://127.0.0.1:8080'


def matching_server(directory):
    try:
        # Local control must not pass through an inherited organization HTTP proxy.
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(BASE+'/api/health',timeout=1) as response:body=json.load(response)
        return body.get('app')=='toshdotau-navbat' and body.get('instance')==instance_id(directory)
    except (OSError,ValueError):return False


def first_setup(directory):
    if has_admin(directory):return True
    import tkinter as tk
    from tkinter import ttk,messagebox,filedialog
    root=tk.Tk();root.title('TO‘SDO‘TAU — Elektron navbat tizimi');root.geometry('560x370')
    frame=ttk.Frame(root,padding=24);frame.pack(fill='both',expand=True);result=[]
    ttk.Label(frame,text='Birinçi oçiliş: administrator parolini yarating.',font=('Segoe UI',12,'bold')).pack(pady=12)
    ttk.Label(frame,text='Parol — kamida 12 belgi').pack(anchor='w');first=ttk.Entry(frame,show='*');first.pack(fill='x',pady=6)
    ttk.Label(frame,text='Parolni takrorlang').pack(anchor='w');second=ttk.Entry(frame,show='*');second.pack(fill='x',pady=6)
    def create():
        try:
            validate_password(first.get(),second.get())
            import app
            app.initialize(first.get())
        except Exception as exc:messagebox.showerror('TOShDOTAU',str(exc),parent=root);return
        result.append(True);root.destroy()
    ttk.Button(frame,text='Saqlaş va oçiş',command=create).pack(fill='x',pady=10)
    def restore():
        source=filedialog.askdirectory(title='Eski data papkasini tanlang',parent=root)
        if not source:return
        try:
            from tools.prepare_install_data import copy_data
            copy_data(source,directory)
        except Exception as exc:messagebox.showerror('TOShDOTAU',str(exc),parent=root);return
        result.append(True);root.destroy()
    ttk.Button(frame,text='Eski data papkasidan köçiriş',command=restore).pack(fill='x')
    root.mainloop();return bool(result)


class ServerSession:
    """One owned server, stopped and joined before releasing its database lock."""
    def __init__(self,directory,port=8080,desktop_control=None):
        import threading
        self.directory=directory;self.port=port;self.desktop_control=desktop_control;self.stop=threading.Event();self.thread=None;self.error=None
    def start(self):
        import socket,threading,app,printer_adapter
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1',self.port))==0:raise RuntimeError('8080 port band. Eski app.py yoki TOShDOTAU serverini avval yoping.')
        app.initialize();printer_adapter.apply_kiosk_preset(app.connect)
        def serve():
            try:app.run_server('0.0.0.0',self.port,self.stop,self.desktop_control)
            except Exception as exc:self.error=exc
        self.thread=threading.Thread(target=serve,name='navbat-owned-server');self.thread.start()
        for _ in range(100):
            if self.error:raise self.error
            try:
                with urllib.request.build_opener(urllib.request.ProxyHandler({})).open('http://127.0.0.1:'+str(self.port)+'/api/health',timeout=.5) as r:
                    if json.load(r).get('instance')==instance_id(self.directory):return
            except (OSError,ValueError):pass
            time.sleep(.1)
        raise RuntimeError('Server ishga tuşmadi. Diagnostika jurnalini tekshiring.')
    def close(self):
        self.stop.set()
        if self.thread:self.thread.join()


def gui(manage=False):
    import runtime,native_window,app
    directory=data_directory();control=directory.parent/'desktop_session'
    try:lock=runtime.InstanceLock(control);lock.__enter__()
    except RuntimeError:
        if manage:(control/'open-admin').write_text('open',encoding='ascii')
        if os.name=='nt':
            import ctypes
            hwnd=ctypes.windll.user32.FindWindowW(None,native_window.TITLE)
            if hwnd:ctypes.windll.user32.ShowWindow(hwnd,9);ctypes.windll.user32.SetForegroundWindow(hwnd)
        return
    session=ServerSession(directory,desktop_control=control);children=[];stop_file=control/'close-views'
    try:
        if not native_window.runtime_available():raise RuntimeError('Microsoft Edge WebView2 Runtime topilmadi. Setup.exe orqali örnating; WEBVIEW2_RUNTIME.md yöriqnomasi ham mavjud.')
        if not first_setup(directory):return
        stop_file.unlink(missing_ok=True);(control/'open-admin').unlink(missing_ok=True)
        session.start()
        def admin():
            children[:]=[child for child in children if child.poll() is None]
            if children:return
            environment=dict(os.environ,NAVBAT_CLOSE_FILE=str(stop_file))
            with (directory/'desktop-ui.log').open('ab') as log:
                children.append(subprocess.Popen(launch_command('--view','admin'),env=environment,stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)))
        native_window.run_view(BASE,'admin' if manage else 'terminal',open_admin=admin,request_file=control/'open-admin')
    finally:
        stop_file.write_text('close',encoding='ascii')
        for child in children:
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=5)
        session.close();lock.__exit__(None,None,None)


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
    parser=argparse.ArgumentParser();parser.add_argument('--server',action='store_true');parser.add_argument('--kiosk',action='store_true');parser.add_argument('--self-test');parser.add_argument('--manage',action='store_true');parser.add_argument('--view',choices=['admin','staff','tv']);parser.add_argument('--native-self-test')
    args=parser.parse_args()
    if args.self_test:raise SystemExit(self_test(args.self_test))
    if args.native_self_test:
        from native_smoke import test_native
        raise SystemExit(test_native(args.native_self_test))
    os.environ['NAVBAT_DATA']=str(data_directory())
    import app
    if args.server:
        app.initialize()
        import printer_adapter
        printer_adapter.apply_kiosk_preset(app.connect)
        app.run_server('0.0.0.0',8080)
    elif args.view:
        import native_window
        native_window.run_view(BASE,args.view,close_file=os.environ.get('NAVBAT_CLOSE_FILE'))
    else:gui(args.manage)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        if '--server' in sys.argv:raise
        import tkinter as tk
        from tkinter import messagebox
        root=tk.Tk();root.withdraw();messagebox.showerror('TOShDOTAU — xato',str(exc));root.destroy()
        raise SystemExit(1)
