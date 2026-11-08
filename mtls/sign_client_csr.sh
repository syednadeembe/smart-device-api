#!/bin/sh

set -eu

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s CLIENT_CSR_FILE\n' "$0" >&2
  exit 2
fi

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
OUTPUT_DIR=${MTLS_OUTPUT_DIR:-"$SCRIPT_DIR/generated"}
CLIENT_CSR=$1

if [ ! -s "$CLIENT_CSR" ]; then
  printf 'Client CSR file does not exist or is empty: %s\n' "$CLIENT_CSR" >&2
  exit 1
fi
if [ ! -s "$OUTPUT_DIR/ca.crt" ] || [ ! -s "$OUTPUT_DIR/ca.key" ]; then
  printf 'Create the demo CA first by running create_server_credentials.sh.\n' >&2
  exit 1
fi

openssl req -in "$CLIENT_CSR" -noout -verify
openssl x509 -req \
  -in "$CLIENT_CSR" \
  -CA "$OUTPUT_DIR/ca.crt" \
  -CAkey "$OUTPUT_DIR/ca.key" \
  -CAcreateserial \
  -out "$OUTPUT_DIR/client.crt" \
  -days 7 -sha256 \
  -extfile "$SCRIPT_DIR/client.ext"

chmod 600 "$OUTPUT_DIR/client.crt"
printf 'Signed the Client certificate: %s/client.crt\n' "$OUTPUT_DIR"
printf 'Transfer client.crt and ca.crt to the Client; never transfer ca.key.\n'
