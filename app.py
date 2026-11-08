"""A tiny Smart Device API used by the XLabs networking project."""

from __future__ import annotations

import json
import os
import random
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit


AUTH_MODE = os.environ.get("AUTH_MODE", "off").strip().lower()
if AUTH_MODE not in {"off", "jwt"}:
    raise SystemExit("AUTH_MODE must be 'off' or 'jwt'")

if AUTH_MODE == "jwt":
    try:
        from jwt_auth.auth import TokenRejected, validate_bearer_token, validate_configuration
    except ImportError as error:
        raise SystemExit(
            "JWT mode needs PyJWT. Install the project requirements with: "
            "python3 -m pip install -r requirements.txt"
        ) from error
else:
    TokenRejected = None  # type: ignore[assignment,misc]
    validate_bearer_token = None
    validate_configuration = None


class SmartDeviceHandler(BaseHTTPRequestHandler):
    server_version = "SmartDeviceAPI/0.1"

    def do_GET(self) -> None:
        path = urlsplit(self.path).path

        if path == "/healthz":
            self._send_json(200, {"status": "ok"})
            return

        if path == "/temperature":
            if AUTH_MODE == "jwt":
                try:
                    validate_bearer_token(self.headers.get("Authorization"))
                except TokenRejected as error:
                    self._send_json(
                        401,
                        {"error": "unauthorized", "message": str(error)},
                        {"WWW-Authenticate": "Bearer"},
                    )
                    return

            cpu_temperature = round(random.uniform(0.0, 100.0), 1)
            gpu_temperature = round(random.uniform(0.0, 100.0), 1)
            self._send_json(
                200,
                {
                    "device": os.environ.get("DEVICE_NAME", "smart-device"),
                    "cpu_temperature_c": cpu_temperature,
                    "gpu_temperature_c": gpu_temperature,
                    "unit": "celsius",
                    "ideal_range_c": {"min": 40.0, "max": 60.0},
                },
            )
            return

        self._send_json(404, {"error": "not_found", "message": "Try /healthz or /temperature."})

    def _send_json(
        self,
        status: int,
        payload: dict[str, Any],
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"{self.address_string()} - {format_string % args}")


def main() -> None:
    if AUTH_MODE == "jwt":
        validate_configuration()

    host = os.environ.get("HOST", "0.0.0.0")
    try:
        port = int(os.environ.get("PORT", "8080"))
    except ValueError as error:
        raise SystemExit("PORT must be a number between 1 and 65535") from error

    if not 1 <= port <= 65535:
        raise SystemExit("PORT must be a number between 1 and 65535")

    server = ThreadingHTTPServer((host, port), SmartDeviceHandler)
    tls_configured = any(
        os.environ.get(name)
        for name in ("TLS_CERT_FILE", "TLS_KEY_FILE", "TLS_CA_FILE")
    )
    if tls_configured:
        try:
            from mtls.context import create_server_context
            context = create_server_context()
            server.socket = context.wrap_socket(server.socket, server_side=True)
        except (OSError, ValueError) as error:
            server.server_close()
            raise SystemExit(f"Could not configure HTTPS/mTLS: {error}") from error
        print(f"Smart Device API serving HTTPS with required client certificates on {host}:{port}")
    else:
        print(f"Smart Device API serving HTTP on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Smart Device API")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
