import hashlib
import ipaddress
import os
import socket
from urllib.parse import urlparse

import requests
import yaml
from flask import Flask, jsonify, request

app = Flask(__name__)

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

LEDGER = [
    {"id": "txn_1001", "token": "tok_6f4d26d63d7266d8f73d8ae4", "amount": 4200, "currency": "USD", "status": "captured"},
    {"id": "txn_1002", "token": "tok_80a7f848b284f7f70d2f7b13", "amount": 1899, "currency": "EUR", "status": "refunded"},
]


def _validate_pan(pan):
    digits_only = pan.isdigit()
    return digits_only and 12 <= len(pan) <= 19


def _is_public_hostname(hostname):
    try:
        addresses = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False

    for address in addresses:
        candidate = ipaddress.ip_address(address[4][0])
        if (
            candidate.is_private
            or candidate.is_loopback
            or candidate.is_link_local
            or candidate.is_multicast
            or candidate.is_reserved
            or candidate.is_unspecified
        ):
            return False
    return True


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/ready")
def ready():
    return jsonify(status="ready")


@app.route("/tokenize", methods=["POST"])
def tokenize():
    payload = request.get_json(silent=True) or {}
    pan = payload.get("pan", "")
    if not _validate_pan(pan):
        return jsonify(error="invalid pan"), 400
    token = "tok_" + hashlib.sha256(pan.encode()).hexdigest()[:24]
    return jsonify(token=token, last4=pan[-4:])


@app.route("/transactions")
def transactions():
    return jsonify(transactions=LEDGER)


@app.route("/import", methods=["POST"])
def import_config():
    config = yaml.safe_load(request.data) or {}
    return jsonify(loaded=str(config))


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return jsonify(error="only https URLs are allowed"), 400
    if not _is_public_hostname(parsed.hostname):
        return jsonify(error="target host is not allowed"), 400
    resp = requests.get(url, timeout=5)
    return jsonify(status_code=resp.status_code, body=resp.text[:2048])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
