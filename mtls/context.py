"""Create a server TLS context that requires a client certificate."""

from __future__ import annotations

import os
import ssl


def create_server_context() -> ssl.SSLContext:
    certificate_file = os.environ.get("TLS_CERT_FILE")
    private_key_file = os.environ.get("TLS_KEY_FILE")
    ca_file = os.environ.get("TLS_CA_FILE")

    missing = [
        name
        for name, value in (
            ("TLS_CERT_FILE", certificate_file),
            ("TLS_KEY_FILE", private_key_file),
            ("TLS_CA_FILE", ca_file),
        )
        if not value
    ]
    if missing:
        raise ValueError(f"Set all required TLS settings: {', '.join(missing)}")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(certfile=certificate_file, keyfile=private_key_file)
    context.load_verify_locations(cafile=ca_file)
    context.verify_mode = ssl.CERT_REQUIRED
    return context
