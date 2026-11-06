"""Windows WebView2 host; no browser process/UI is launched by this module."""
from pathlib import Path
import os
import threading
import time

TITLE='TO‘SDO‘TAU — Elektron navbat tizimi'
ROUTES={'terminal':'/','admin':'/admin','staff':'/staff','tv':'/tv?autostart=1'}


def runtime_available():
    if os.name!='nt':return False
    import winreg
    key=r'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}'
    for hive in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
        for mode in (winreg.KEY_WOW64_32KEY,winreg.KEY_WOW64_64KEY):
            try:
                with winreg.OpenKey(hive,key,0,winreg.KEY_READ|mode) as item:
                    version=winreg.QueryValueEx(item,'pv')[0]
                    if version and version!='0.0.0.0':return True
            except OSError:pass
    return False


def admin_password_ok(name,value):
    import app,hmac
    with app.connect() as c:row=c.execute("SELECT * FROM users WHERE name=? AND role='admin' AND enabled=1",(name,)).fetchone()
    return bool(row and hmac.compare_digest(row['hash'],app.password(value,row['salt'])))


def authorize_exit(parent):
    """Native modal authentication; passwords never enter a JS bridge or a log."""
    from System.Drawing import Size,Point
    from System.Windows.Forms import Form,Label,TextBox,Button,DialogResult,FormStartPosition,FormBorderStyle
    form=Form();form.Text='Administrator tasdiği';form.ClientSize=Size(370,200);form.StartPosition=FormStartPosition.CenterParent;form.FormBorderStyle=FormBorderStyle.FixedDialog;form.MaximizeBox=False;form.MinimizeBox=False
    fields=[]
    for index,(label,value,password) in enumerate([('Login','admin',False),('Parol','',True)]):
        title=Label();title.Text=label;title.Location=Point(20,18+index*55);title.Size=Size(70,25);form.Controls.Add(title)
        field=TextBox();field.Text=value;field.Location=Point(95,16+index*55);field.Size=Size(250,28);field.UseSystemPasswordChar=password;form.Controls.Add(field);fields.append(field)
    status=Label();status.Location=Point(20,120);status.Size=Size(330,25);form.Controls.Add(status)
    ok=Button();ok.Text='Yopiş';ok.Location=Point(170,155);form.Controls.Add(ok)
    cancel=Button();cancel.Text='Bekor qiliş';cancel.Location=Point(260,155);cancel.DialogResult=DialogResult.Cancel;form.Controls.Add(cancel)
    def check(sender,args):
        if admin_password_ok(str(fields[0].Text),str(fields[1].Text)):form.DialogResult=DialogResult.OK;form.Close()
        else:status.Text='Login yoki parol notoğri';fields[1].Clear()
    ok.Click+=check;form.AcceptButton=ok;form.CancelButton=cancel
    try:return form.ShowDialog(parent)==DialogResult.OK
    finally:fields[1].Clear();form.Dispose()


def run_view(base,role='terminal',open_admin=None,close_file=None,request_file=None,smoke=None):
    import webview
    webview.settings['ALLOW_DOWNLOADS']=True
    webview.settings['ALLOW_FILE_URLS']=False
    webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER']=False
    webview.settings['IGNORE_SSL_ERRORS']=False
    window=webview.create_window(TITLE,base+ROUTES[role],fullscreen=role=='terminal',width=1280,height=800,min_size=(800,600),background_color='#102D54')
    ending=threading.Event()
    def closing():
        if role=='terminal' and smoke is None:
            try:
                if not authorize_exit(window.native):return False
            except Exception:
                import logging
                logging.getLogger('navbat').exception('Administrator exit authentication failed')
                return False
        ending.set();return True
    window.events.closing+=closing
    def loaded():
        if role=='terminal':window.run_js("document.addEventListener('keydown',function(e){if(e.key==='F10'){e.preventDefault();fetch('/api/desktop/open-admin',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})}if(e.key==='F11'){e.preventDefault();fetch('/api/desktop/toggle-screen',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})}})")
    window.events.loaded+=loaded
    def monitor():
        if smoke:
            try:smoke(window,webview)
            finally:ending.set();window.destroy()
            return
        while not ending.wait(.5):
            if close_file and Path(close_file).exists():window.destroy();return
            if request_file and Path(request_file).exists():
                Path(request_file).unlink(missing_ok=True)
                if open_admin:open_admin()
            if request_file and Path(request_file).with_name('toggle-screen').exists():
                Path(request_file).with_name('toggle-screen').unlink(missing_ok=True);window.toggle_fullscreen()
    icon=Path(__file__).with_name('university.ico')
    webview.start(monitor,gui='edgechromium',debug=False,private_mode=True,icon=str(icon) if icon.is_file() else None)
    ending.set()
