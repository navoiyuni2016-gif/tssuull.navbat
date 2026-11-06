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
            thread=threading.Thread(target=server.serve_forever);thread.start();base='http://127.0.0.1:'+str(server.server_port)
            def verify(window,webview):
                nonlocal result
                try:
                    assert webview.renderer=='edgechromium',webview.renderer
                    for _ in range(150):
                        count=window.evaluate_js("document.querySelectorAll('#services .service-card').length")
                        if count==5:break
                        time.sleep(.1)
                    assert count==5,count
                    assert window.native is not None
                    assert window.evaluate_js('document.title')=='TOŞDÖTAU — elektron navbat tizimi'
                    window.load_url(base+'/admin')
                    for _ in range(100):
                        if window.evaluate_js("!!document.querySelector('.login-form')"):break
                        time.sleep(.1)
                    assert window.evaluate_js("!!document.querySelector('.login-form')")
                    result={'ok':True,'renderer':webview.renderer,'services':count,'admin_login':True,'native_window':True}
                except Exception:result={'ok':False,'error':traceback.format_exc()}
            try:native_window.run_view(base,smoke=verify)
            finally:server.shutdown();server.server_close();thread.join()
    except Exception:result={'ok':False,'error':traceback.format_exc()}
    Path(destination).write_text(json.dumps(result),encoding='utf-8');return 0 if result.get('ok') else 1
