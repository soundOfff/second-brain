#!/usr/bin/env python3
"""Second Brain — localhost clip helper (capture-bridge GUI surface #4).

A tiny, stdlib-only HTTP endpoint the Chrome "Clip to Brain" extension POSTs to, since a
browser cannot run a shell script directly. It only ever shells out to bin/brain-clip.sh
with an explicit argument list (no shell string), binds to 127.0.0.1 only, and does no
synthesis — it just deposits the raw source, exactly like the CLI. Run it under launchd
(bin/launchd/com.secondbrain.clipserver.plist, KeepAlive) so the button always works.

    brain-clip-server.py [--port 8766]

POST /clip   body: form-encoded or JSON  { url? , text? , type? , title? }
GET  /        health check / identity
"""
import json
import os
import subprocess
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
CLIP = os.path.join(HERE, "brain-clip.sh")
# brain-clip.sh needs python3 (often in Homebrew) + curl on PATH.
ENV = dict(os.environ, PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", ""))
ALLOWED_TYPES = {"article", "pdf", "transcript", "screenshot", "note", "data"}


def run_clip(fields):
    url = (fields.get("url") or "").strip()
    text = (fields.get("text") or "").strip()
    arg = url or text
    if not arg:
        return False, "nothing to clip (no url or text)"
    args = [CLIP]
    t = (fields.get("type") or "").strip()
    if t in ALLOWED_TYPES:
        args += ["--type", t]
    title = (fields.get("title") or "").strip()
    if title:
        args += ["--title", title]
    if url and text:           # both given: treat text as a note with the url attached
        args += ["--url", url]
        arg = text
    args.append(arg)
    try:
        p = subprocess.run(args, capture_output=True, text=True, env=ENV, timeout=60)
    except Exception as e:                       # noqa: BLE001
        return False, f"clip failed: {e}"
    out = (p.stdout + p.stderr).strip()
    wrote = [ln for ln in out.splitlines() if ln.startswith("wrote ")]
    if p.returncode == 0:
        return True, (wrote[-1] if wrote else "clipped")
    return False, (out.splitlines() or ["clip failed"])[-1]


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        if self.path.rstrip("/") in ("", "/health"):
            self._send(200, {"ok": True, "service": "brain-clip-server", "clip": CLIP})
        else:
            self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/clip":
            return self._send(404, {"ok": False, "error": "not found"})
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip()
        try:
            if ctype == "application/json":
                fields = json.loads(raw or "{}")
            else:
                fields = {k: v[-1] for k, v in urllib.parse.parse_qs(raw).items()}
        except Exception:                         # noqa: BLE001
            return self._send(400, {"ok": False, "error": "bad request body"})
        ok, msg = run_clip(fields)
        self._send(200 if ok else 422, {"ok": ok, "message": msg})

    def log_message(self, *a):                    # quiet; launchd captures nothing useful
        pass


def main():
    port = 8766
    argv = sys.argv[1:]
    if "--port" in argv:
        port = int(argv[argv.index("--port") + 1])
    if not os.access(CLIP, os.X_OK):
        sys.exit(f"brain-clip.sh not executable at {CLIP}")
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"brain-clip-server on http://127.0.0.1:{port}  (clip: {CLIP})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
