import json
import subprocess
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


def start_server(html: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())

    server = HTTPServer(('localhost', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, server.server_address[1]


def test_cli(tmp_path):
    html = '<html><header></header><h1>Test</h1></html>'
    server, port = start_server(html)
    out_file = tmp_path / 'result.json'
    cmd = [sys.executable, 'ai_readiness_checker.py', f'http://localhost:{port}', '-o', str(out_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    server.shutdown()
    assert result.returncode == 0
    data = json.loads(out_file.read_text())
    assert data['url'] == f'http://localhost:{port}'
    assert data['total'] == 7
