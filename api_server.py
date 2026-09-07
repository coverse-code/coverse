import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT, "server_data.json")


def ensure_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "users": [],
                "groups": [],
                "subjects": [],
                "grades": [],
                "attendance": [],
                "notices": []
            }, f, ensure_ascii=False, indent=2)


def read_data():
    ensure_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "users": [],
            "groups": [],
            "subjects": [],
            "grades": [],
            "attendance": [],
            "notices": []
        }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            data = read_data()
            self.send_json({"ok": True, "data": data})
            return
        if parsed.path == "/api/health":
            self.send_json({"ok": True, "status": "running"})
            return
        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length else ""

        if parsed.path == "/api/save":
            try:
                data = json.loads(body or "{}")
            except Exception:
                self.send_json({"ok": False, "message": "Bad JSON"}, 400)
                return

            save_data(data)
            self.send_json({"ok": True})
            return

        self.send_error(404)

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    ensure_data()
    server = ThreadingHTTPServer(("127.0.0.1", 8001), Handler)
    print("Legacy backend restricted to http://127.0.0.1:8001")
    server.serve_forever()
