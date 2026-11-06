# Smart Device API

A small Python service for **The Journey of a Packet** XLabs networking project. It simulates CPU and GPU temperatures for an R&D team's data-center monitoring proof of concept. The Smart Device Server runs this API; the Dashboard Client requests the readings. The team uses 40–60°C as its ideal range for this learning project.

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

## Learning path

This is the unauthenticated HTTP starting point for the project. Later phases can extend this same API to check JWT bearer tokens and use HTTPS with mutual TLS (mTLS). Those security features are not enabled in this starter version.

This service is an educational proof of concept. It uses plain HTTP and has no authentication; keep it inside the isolated project network and do not expose it to the public internet or use it for real device data.
