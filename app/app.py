import secrets

from flask import Flask, jsonify, request

app = Flask(__name__)

LEDGER = [
    {"id": "txn_1001", "token": "tok_6f4d26d63d7266d8f73d8ae4", "amount": 4200, "currency": "USD", "status": "captured"},
    {"id": "txn_1002", "token": "tok_80a7f848b284f7f70d2f7b13", "amount": 1899, "currency": "EUR", "status": "refunded"},
]


def _validate_pan(pan):
    digits_only = pan.isdigit()
    return digits_only and 12 <= len(pan) <= 19


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
    token = "tok_" + secrets.token_hex(12)
    return jsonify(token=token, last4=pan[-4:])


@app.route("/transactions")
def transactions():
    return jsonify(transactions=LEDGER)
