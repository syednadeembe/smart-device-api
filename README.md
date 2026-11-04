# Smart Device API

A small Python service for **The Journey of a Packet** XLabs networking project. The Smart Device acts as the server; the Dashboard acts as the client and requests its temperature reading.

This service uses Python's standard library and has no third-party package requirements. It adapts the lightweight `BaseHTTPRequestHandler` pattern already used in the XLabs Networking Hub troubleshooting lab.

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

The temperature endpoint returns JSON similar to:

```json
{"device":"smart-device","temperature_c":22.5,"unit":"celsius"}
```

## Configuration

The defaults work for the project. Optional environment variables are:

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Address the service listens on |
| `PORT` | `8080` | TCP port for HTTP requests |
| `DEVICE_NAME` | `smart-device` | Device name returned in the reading |
| `TEMPERATURE_C` | `22.5` | Example temperature in Celsius |

For example:

```sh
DEVICE_NAME=lab-sensor TEMPERATURE_C=24.1 PORT=8081 python3 app.py
```

## Learning path

This is the unauthenticated HTTP starting point for the project. Later phases can extend this same API to check JWT bearer tokens and use HTTPS with mutual TLS (mTLS). Those security features are not enabled in this starter version.

This service is an educational proof of concept. It uses plain HTTP and has no authentication; keep it inside the isolated project network and do not expose it to the public internet or use it for real device data.
