# Smart Device API

A small Python service for **The Journey of a Packet** XLabs networking project. It simulates CPU and GPU temperatures for an R&D team's data-center monitoring proof of concept. The Smart Device Server runs this API; the Dashboard Client requests the readings. The team uses 40–60°C as its ideal range for this learning project.

The baseline service uses Python's standard library and has no third-party package requirements. It adapts the lightweight `BaseHTTPRequestHandler` pattern already used in the XLabs Networking Hub troubleshooting lab. JWT support is isolated in `jwt_auth/`; HTTPS and mutual TLS support are isolated in `mtls/`.

## Run the service

Use Python 3 on the Smart Device Server terminal:

```sh
python3 app.py
```

By default, the service listens on `0.0.0.0:8080`. The `0.0.0.0` address lets another container connect through the Smart Device's network interface.

## Try the endpoints

On the Smart Device Server, check the service locally:

```sh
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8080/temperature
```

After the Dashboard Client can resolve the name `smart-device`, run these commands from the Client terminal:

```sh
curl http://smart-device:8080/healthz
curl http://smart-device:8080/temperature
```

Every request to the temperature endpoint generates new simulated CPU and GPU readings between 0.0°C and 100.0°C. The target range is 40.0°C to 60.0°C; later project phases can use readings outside that range to build alerts. These are sample values, not readings from real hardware, and they do not indicate the real status of your computer or a data center.

The endpoint returns JSON similar to:

```json
{"device":"smart-device","cpu_temperature_c":52.4,"gpu_temperature_c":73.1,"unit":"celsius","ideal_range_c":{"min":40.0,"max":60.0}}
```

Run the request several times to see new values:

```sh
for i in 1 2 3; do curl -s http://127.0.0.1:8080/temperature; echo; done
```

## Configuration

The defaults work for the project. Optional environment variables are:

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Address the service listens on |
| `PORT` | `8080` | TCP port for HTTP requests |
| `DEVICE_NAME` | `smart-device` | Device name returned in the reading |

For example, change the device name or port:

```sh
DEVICE_NAME=compute-node-01 PORT=8081 python3 app.py
```

## Phase 5: protect readings with a JWT

The default app has no authentication, so Phases 1–4 continue to work with `python3 app.py`. For Phase 5, install the JWT library in the Smart Device Server container:

```sh
python3 -m pip install -r requirements.txt
```

Create a demo signing secret in the Server shell and turn on JWT mode:

```sh
export JWT_SECRET="$(openssl rand -hex 32)"
export AUTH_MODE=jwt
nohup python3 app.py > server.log 2>&1 &
```

Keep `JWT_SECRET` on the Server. In the same Server terminal shell, issue a short-lived token:

```sh
python3 -m jwt_auth.issue_token --subject dashboard-client --lifetime 300
```

Copy only the printed token to the Dashboard Client. Requests to `/temperature` need an `Authorization: Bearer <token>` header; requests without a valid token receive HTTP 401. `/healthz` remains available without a JWT. The API validates the token signature using the fixed HS256 algorithm and requires its issuer, audience, subject, and expiry claims.

A JWT is signed, not encrypted. Phase 5 intentionally demonstrates authorization over the project's isolated HTTP network; do not expose this mode to the public internet. Phase 6 adds HTTPS and client-certificate authentication.

## Phase 6: use HTTPS with mutual TLS

Stop the Phase 5 HTTP server before starting the HTTPS server. Generate a Server certificate, a local CA certificate, and a Client certificate signed by that CA. Keep the CA private key on the Server and generate the Client private key inside the Client container. Transfer only the Client's certificate signing request to the Server for signing; never copy the Client private key to the Server.

Start the API with JWT still enabled and the TLS files configured:

```sh
export AUTH_MODE=jwt
export TLS_CERT_FILE="$HOME/smart-device-api/mtls/generated/server.crt"
export TLS_KEY_FILE="$HOME/smart-device-api/mtls/generated/server.key"
export TLS_CA_FILE="$HOME/smart-device-api/mtls/generated/ca.crt"
export PORT=8443
python3 "$HOME/smart-device-api/app.py"
```

The HTTPS listener requires a client certificate signed by the configured CA. It also requires the Client to trust the Server CA and verify that the Server certificate is for `smart-device`. Use `curl --cacert`, `--cert`, and `--key`; do not use `-k` or disable verification. Include the JWT bearer token as well: mTLS identifies the Client certificate and protects the transport, while JWT authorizes the API request.

Create the demo CA and Server certificate on the Server:

```sh
sh mtls/create_server_credentials.sh
```

Generate the Client private key and CSR on the Client. The private key stays there:

```sh
mkdir -p "$HOME/mtls-client"
openssl req -newkey rsa:2048 -nodes \
  -keyout "$HOME/mtls-client/client.key" \
  -out "$HOME/mtls-client/client.csr" \
  -subj "/CN=dashboard-client"
```

Copy the public CSR text to the Server and save it as `mtls/generated/client.csr`. Sign it on the Server:

```sh
sh mtls/sign_client_csr.sh "$HOME/smart-device-api/mtls/generated/client.csr"
```

Copy only `client.crt` and `ca.crt` back to the Client's `mtls-client` folder. Do not copy `client.key`, `ca.key`, or `server.key` between containers. Generated credentials stay in the isolated project containers and are ignored by Git.

## Learning path

This is the unauthenticated HTTP starting point for the project. Later phases enable JWT bearer-token checks and HTTPS with mutual TLS (mTLS) in separate modules while preserving this default startup mode.

This service is an educational proof of concept. It uses plain HTTP and has no authentication; keep it inside the isolated project network and do not expose it to the public internet or use it for real device data.
