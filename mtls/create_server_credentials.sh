#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
OUTPUT_DIR=${MTLS_OUTPUT_DIR:-"$SCRIPT_DIR/generated"}

umask 077
mkdir -p "$OUTPUT_DIR"

openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout "$OUTPUT_DIR/ca.key" \
  -out "$OUTPUT_DIR/ca.crt" \
  -days 7 -sha256 \
  -subj "/CN=XLabs Smart Device Demo CA" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"

openssl req -newkey rsa:2048 -nodes \
  -keyout "$OUTPUT_DIR/server.key" \
  -out "$OUTPUT_DIR/server.csr" \
  -subj "/CN=smart-device"

openssl x509 -req \
  -in "$OUTPUT_DIR/server.csr" \
  -CA "$OUTPUT_DIR/ca.crt" \
  -CAkey "$OUTPUT_DIR/ca.key" \
  -CAcreateserial \
  -out "$OUTPUT_DIR/server.crt" \
  -days 7 -sha256 \
  -extfile "$SCRIPT_DIR/server.ext"

chmod 600 "$OUTPUT_DIR/ca.key" "$OUTPUT_DIR/server.key"
printf 'Created the demo CA and Server certificate in %s\n' "$OUTPUT_DIR"
printf 'Keep ca.key and server.key on the Server. Share only ca.crt with the Client.\n'
