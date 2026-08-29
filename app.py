from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict

from dashboard_simulator import VirtualCockpitController

HOST = "127.0.0.1"
PORT = 5001
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

controller = VirtualCockpitController()


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            self.serve_file(STATIC_DIR / "index.html")
        elif self.path == "/api/status":
            self.send_json(controller.get_status())
        else:
            file_path = STATIC_DIR / self.path.lstrip("/")
            if file_path.exists() and file_path.is_file():
                self.serve_file(file_path)
            else:
                self.send_error(404, "Not found")

    def do_POST(self) -> None:
        if self.path != "/api/control":
            self.send_error(404, "Not found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        payload = json.loads(raw.decode("utf-8") or "{}")

        if "rpm" in payload:
            controller.update_rpm(int(payload["rpm"]))
        if "speed" in payload:
            controller.update_speed(int(payload["speed"]))
        if "fuel" in payload:
            controller.update_fuel(int(payload["fuel"]))
        if "wiper_mode" in payload:
            controller.set_wiper_mode(str(payload["wiper_mode"]))
        if "indicator" in payload:
            side = str(payload["indicator"]).lower()
            active = bool(payload.get("active", False))
            controller.set_indicator(side, active)

        self.send_json(controller.get_status())

    def serve_file(self, file_path: Path) -> None:
        content = file_path.read_bytes()
        self.send_response(200)
        if file_path.suffix == ".html":
            self.send_header("Content-Type", "text/html; charset=utf-8")
        elif file_path.suffix == ".css":
            self.send_header("Content-Type", "text/css; charset=utf-8")
        elif file_path.suffix == ".js":
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
        else:
            self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, body: Dict[str, object]) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:
        return


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), DashboardHandler)
    print(f"Virtual cockpit dashboard running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server...")
    finally:
        server.server_close()
