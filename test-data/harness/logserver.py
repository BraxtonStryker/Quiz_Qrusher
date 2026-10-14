import http.server, sys, os
ROOT, OUT = sys.argv[1], sys.argv[2]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a): pass
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0)); body = self.rfile.read(n)
        open(OUT, 'wb').write(body); self.send_response(204); self.end_headers()
http.server.ThreadingHTTPServer(('127.0.0.1', 8767), H).serve_forever()
