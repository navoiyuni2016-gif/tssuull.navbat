"""Native Windows Service Control Manager adapter, no third-party packages."""
import ctypes
from ctypes import wintypes
import logging
import os
from pathlib import Path
import sys
import threading


def main():
    if os.name!='nt':raise SystemExit('Bu modul faqat Windows uchun')
    import app
    api=ctypes.WinDLL('advapi32',use_last_error=True)
    stop=threading.Event()
    class Status(ctypes.Structure):
        _fields_=[('service_type',wintypes.DWORD),('state',wintypes.DWORD),('controls',wintypes.DWORD),('win32_exit',wintypes.DWORD),('specific_exit',wintypes.DWORD),('checkpoint',wintypes.DWORD),('wait_hint',wintypes.DWORD)]
    HANDLER=ctypes.WINFUNCTYPE(wintypes.DWORD,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.LPVOID)
    MAIN=ctypes.WINFUNCTYPE(None,wintypes.DWORD,ctypes.POINTER(wintypes.LPWSTR))
    class Entry(ctypes.Structure):_fields_=[('name',wintypes.LPWSTR),('main',MAIN)]
    api.RegisterServiceCtrlHandlerExW.argtypes=[wintypes.LPCWSTR,HANDLER,wintypes.LPVOID]
    api.RegisterServiceCtrlHandlerExW.restype=wintypes.HANDLE
    api.SetServiceStatus.argtypes=[wintypes.HANDLE,ctypes.POINTER(Status)]
    api.SetServiceStatus.restype=wintypes.BOOL
    api.StartServiceCtrlDispatcherW.argtypes=[ctypes.POINTER(Entry)]
    api.StartServiceCtrlDispatcherW.restype=wintypes.BOOL
    handle=None
    def report(state,code=0):
        status=Status(16,state,5 if state==4 else 0,code,0,1 if state in (2,3) else 0,15000 if state in (2,3) else 0)
        if not api.SetServiceStatus(handle,ctypes.byref(status)):raise ctypes.WinError(ctypes.get_last_error())
    @HANDLER
    def handler(control,event,data,context):
        if control in (1,5):report(3);stop.set()
        return 0
    @MAIN
    def service(argc,argv):
        nonlocal handle
        handle=api.RegisterServiceCtrlHandlerExW('UniversitetNavbat',handler,None)
        if not handle:return
        report(2)
        try:
            import json
            settings_path=Path(__file__).parent/'windows'/'server.json'
            config=json.loads(settings_path.read_text()) if settings_path.exists() else {'host':'0.0.0.0','port':8080}
            app.initialize();report(4)
            app.run_server(config['host'],int(config['port']),stop)
            report(1)
        except Exception:
            app.DATA.mkdir(parents=True,exist_ok=True)
            import traceback
            (app.DATA/'service-error.log').write_text(traceback.format_exc()[-32000:],encoding='utf-8')
            report(1,1066)
    table=(Entry*2)();table[0]=Entry('UniversitetNavbat',service)
    if not api.StartServiceCtrlDispatcherW(table):raise ctypes.WinError(ctypes.get_last_error())

if __name__=='__main__':main()
