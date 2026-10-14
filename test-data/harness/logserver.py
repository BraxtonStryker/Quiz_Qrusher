"""v3.0 - static server for the harness: serves ROOT, and a POST to any path writes the body to OUT.

Usage: python -I logserver.py <root> <out-file>      (listens on 127.0.0.1:8767)

/_variant/<name>/<path> serves <path> with a script injected at the top of <head>, to fake a browser:
  nofsa  - no showDirectoryPicker (Firefox/Safari-like: the unsupported-browser notice shows)
  noidb  - no IndexedDB (tests the localStorage fallback)
"""
import http.server, os, sys

ROOT, OUT = sys.argv[1], sys.argv[2]
VARIANTS = {
    "nofsa": b"<script>try{delete Window.prototype.showDirectoryPicker;delete window.showDirectoryPicker;}catch(e){}</script>",
    "noidb": b"<script>try{Object.defineProperty(window,'indexedDB',{value:undefined});}catch(e){}</script>",
}


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass

    def do_GET(self):
        parts = self.path.split("?")[0].split("/")
        if len(parts) > 3 and parts[1] == "_variant" and parts[2] in VARIANTS:
            rel = "/".join(parts[3:])
            full = os.path.realpath(os.path.join(ROOT, rel))
            if not full.startswith(os.path.realpath(ROOT)) or not os.path.isfile(full):
                self.send_error(404); return
            body = open(full, "rb").read()
            if rel.endswith(".html"):
                body = body.replace(b"<head>", b"<head>" + VARIANTS[parts[2]], 1)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8" if rel.endswith(".html") else self.guess_type(full))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        open(OUT, "wb").write(body)
        self.send_response(204)
        self.end_headers()


http.server.ThreadingHTTPServer(("127.0.0.1", 8767), H).serve_forever()
