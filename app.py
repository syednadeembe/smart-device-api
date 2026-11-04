"""A tiny Smart Device API used by the XLabs networking project."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit


class SmartDeviceHandler(BaseHTTPRequestHandler):
    server_version = "SmartDeviceAPI/0.1"

    def do_GET(self) -> None:
        path = urlsplit(self.path).path

        if path == "/healthz":
            self._send_json(200, {"status": "ok"})
            return

        if path == "/temperature":
            self._send_json(
                200,
                {
                    "device": os.environ.get("DEVICE_NAME", "smart-device"),
                    "temperature_c": self._temperature(),
                    "unit": "celsius",
                },
            )
            return

        self._send_json(404, {"error": "not_found", "message": "Try /healthz or /temperature."})

    def _temperature(self) -> float:
        try:
            return float(os.environ.get("TEMPERATURE_C", "22.5"))
        except ValueError:
            return 22.5

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"{self.address_string()} - {format_string % args}")


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    try:
        port = int(os.environ.get("PORT", "8080"))
    except ValueError as error:
        raise SystemExit("PORT must be a number between 1 and 65535") from error

    if not 1 <= port <= 65535:
        raise SystemExit("PORT must be a number between 1 and 65535")

    server = ThreadingHTTPServer((host, port), SmartDeviceHandler)
    print(f"Smart Device API listening on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Smart Device API")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
