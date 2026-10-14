"""v3.0 - screenshot a page in an already-running headless Chrome over the DevTools protocol (stdlib only).

Usage: python -I cdp_shot.py <debug-port> <url-substring> <out.png> [wait-seconds] [width] [height]
Chrome must be started with --remote-debugging-port=<debug-port> and the page loaded. Waits, then captures
the page whose URL contains <url-substring>. Lets a driver page click through the app in real time first
(headless --screenshot uses virtual time, which outruns FileReader).
"""
import base64, json, os, socket, struct, sys, time, urllib.request


def ws_connect(url):
    host_port, path = url[len("ws://"):].split("/", 1)
    host, port = host_port.split(":")
    s = socket.create_connection((host, int(port)))
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall(("GET /%s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n" % (path, host_port, key)).encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        buf += s.recv(4096)
    return s, buf.split(b"\r\n\r\n", 1)[1]


def ws_send(s, text):
    data = text.encode()
    head = bytearray([0x81])
    n = len(data)
    if n < 126:
        head.append(0x80 | n)
    elif n < 65536:
        head.append(0x80 | 126); head += struct.pack(">H", n)
    else:
        head.append(0x80 | 127); head += struct.pack(">Q", n)
    mask = os.urandom(4)
    s.sendall(bytes(head) + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


def ws_recv(s, pending):
    buf = pending
    def need(k):
        nonlocal buf
        while len(buf) < k:
            chunk = s.recv(1 << 20)
            if not chunk:
                raise EOFError
            buf += chunk
    message = b""
    while True:
        need(2)
        fin, n = buf[0] & 0x80, buf[1] & 0x7F
        off = 2
        if n == 126:
            need(4); n = struct.unpack(">H", buf[2:4])[0]; off = 4
        elif n == 127:
            need(10); n = struct.unpack(">Q", buf[2:10])[0]; off = 10
        need(off + n)
        message += buf[off:off + n]
        buf = buf[off + n:]
        if fin:
            return message.decode(), buf


def main():
    port, match, out = sys.argv[1], sys.argv[2], sys.argv[3]
    wait = float(sys.argv[4]) if len(sys.argv) > 4 else 10
    width = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    height = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    target = None
    for _ in range(40):
        try:
            pages = json.load(urllib.request.urlopen("http://127.0.0.1:%s/json" % port))
            target = next((p for p in pages if p.get("type") == "page" and match in p.get("url", "")), None)
            if target:
                break
        except OSError:
            pass
        time.sleep(0.5)
    if not target:
        sys.exit("page not found")
    time.sleep(wait)
    s, pending = ws_connect(target["webSocketDebuggerUrl"])
    msg_id = 0
    def call(method, params=None):
        nonlocal msg_id, pending
        msg_id += 1
        ws_send(s, json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        while True:
            text, pending = ws_recv(s, pending)
            reply = json.loads(text)
            if reply.get("id") == msg_id:
                return reply
    if width and height:
        call("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False})
    shot = call("Page.captureScreenshot", {"format": "png"})
    open(out, "wb").write(base64.b64decode(shot["result"]["data"]))
    print("saved", out)


main()
