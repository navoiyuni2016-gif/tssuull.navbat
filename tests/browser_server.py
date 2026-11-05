from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app
with tempfile.TemporaryDirectory() as directory:
    app.DATA=Path(directory)
    app.initialize('browser-test-password-123')
    server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
    print('READY '+str(server.server_port),flush=True)
    try:server.serve_forever()
    finally:server.server_close()
