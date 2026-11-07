"""Loopback-only standard-library server. Only explicitly registered runs are read."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .run_view import load_run


def make_server(run_dirs, port=8765):
    if not 1 <= len(run_dirs) <= 32:
        raise ValueError("Register 1–32 run directories")
    roots = list(dict.fromkeys(str(Path(p).absolute()) for p in run_dirs))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send_body(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def json(self, status, value):
            self.send_body(status, json.dumps(value, ensure_ascii=False, allow_nan=False).encode(), "application/json; charset=utf-8")

        def do_GET(self):
            allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            if self.headers.get("Host") not in allowed:
                return self.json(403, {"error": "Loopback host required"})
            origin = self.headers.get("Origin")
            if origin and origin not in {"http://" + h for h in allowed}:
                return self.json(403, {"error": "Cross-origin request refused"})
            url = urlsplit(self.path)
            assets = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
                      "/style.css": ("style.css", "text/css")}
            if url.path in assets:
                name, mime = assets[url.path]
                return self.send_body(200, files("prism").joinpath("web", name).read_bytes(), mime + "; charset=utf-8")
            if url.path == "/api/runs":
                return self.json(200, [{"key": str(i), "name": Path(root).name, "source": root} for i, root in enumerate(roots)])
            if url.path == "/api/run":
                key = parse_qs(url.query).get("id", [""])
                if len(key) != 1 or key[0] not in {str(i) for i in range(len(roots))}:
                    return self.json(404, {"error": "Unknown run"})
                try:
                    return self.json(200, load_run(roots[int(key[0])]))
                except (OSError, ValueError, TypeError, KeyError, RecursionError, AttributeError):
                    return self.json(422, {"error": "Не вдалося перевірити запуск: дані відсутні, пошкоджені, завеликі або формат не підтримується. Спробуйте оновити після checkpoint."})
            self.json(404, {"error": "Not found"})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(run_dirs, port=8765, open_browser=False):
    with make_server(run_dirs, port) as server:
        url = f"http://127.0.0.1:{server.server_port}"
        print(f"PRISM viewer: {url} — read-only, Ctrl+C to stop", flush=True)
        if open_browser:
            import webbrowser
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
