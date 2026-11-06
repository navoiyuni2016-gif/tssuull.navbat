"""Frozen WebView2 integration check against the actual local application."""
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import traceback


def test_native(destination):
    result={}
    try:
        with tempfile.TemporaryDirectory() as folder:
            os.environ['NAVBAT_DATA']=folder
            import app,native_window,printer_adapter
            from http.server import ThreadingHTTPServer
            app.DATA=Path(folder);app.initialize('native-smoke-password-123');printer_adapter.apply_kiosk_preset(app.connect)
            server=ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
            control=Path(folder)/'control';control.mkdir();server.desktop_control=control
            thread=threading.Thread(target=server.serve_forever);thread.start();base='http://127.0.0.1:'+str(server.server_port)
            def read(window,expression):
                value=window.run_js('JSON.stringify('+expression+')')
                for _ in range(2):
                    if isinstance(value,str):
                        try:value=json.loads(value)
                        except ValueError:break
                return value
            def verify(window,webview):
                nonlocal result
                try:
                    assert webview.renderer=='edgechromium',webview.renderer
                    window.events.loaded.wait(20)
                    for _ in range(150):
                        count=read(window,"document.querySelectorAll('#services .service-card').length")
                        if count==5:break
                        time.sleep(.1)
                    assert count==5,count
                    assert window.native is not None
                    window.run_js("document.dispatchEvent(new KeyboardEvent('keydown',{key:'F10',bubbles:true}))")
                    for _ in range(50):
                        if (control/'open-admin').exists():break
                        time.sleep(.1)
                    assert (control/'open-admin').exists(),'Native F10 command was not delivered'
                    assert read(window,'document.title')=='TOŞDÖTAU — elektron navbat tizimi'
                    window.load_url(base+'/admin')
                    for _ in range(100):
                        if read(window,"!!document.querySelector('.login-form')"):break
                        time.sleep(.1)
                    assert read(window,"!!document.querySelector('.login-form')")
                    result={'ok':True,'renderer':webview.renderer,'services':count,'admin_login':True,'native_window':True}
                except Exception:result={'ok':False,'error':traceback.format_exc()}
            try:native_window.run_view(base,smoke=verify)
            finally:server.shutdown();server.server_close();thread.join()
    except Exception:result={'ok':False,'error':traceback.format_exc()}
    Path(destination).write_text(json.dumps(result),encoding='utf-8');return 0 if result.get('ok') else 1
