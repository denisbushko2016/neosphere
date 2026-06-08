import os
import json
import secrets
import string
from datetime import datetime

from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials


app = Flask(__name__)

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_sheet():
    service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not service_account_json:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is missing")

    creds_info = json.loads(service_account_json)

    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES,
    )

    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).sheet1


def generate_code():
    alphabet = string.ascii_uppercase + string.digits
    part1 = "".join(secrets.choice(alphabet) for _ in range(4))
    part2 = "".join(secrets.choice(alphabet) for _ in range(4))
    return f"NS-{part1}-{part2}"


def add_access_code(email="", payment_id=""):
    sheet = get_sheet()

    existing_codes = [row.get("code") for row in sheet.get_all_records()]

    while True:
        code = generate_code()
        if code not in existing_codes:
            break

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([
        code,
        "client",
        "",
        "",
        "new",
        email,
        payment_id,
        created_at,
    ])

    return code


@app.route("/", methods=["GET"])
def home():
    return "NeoSphere payment server is running"


@app.route("/yookassa-webhook/<secret>", methods=["POST"])
def yookassa_webhook(secret):
    if secret != WEBHOOK_SECRET:
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "empty payload"}), 400

    event = data.get("event")
    payment_object = data.get("object", {})

    if event != "payment.succeeded":
        return jsonify({"status": "ignored", "event": event}), 200

    payment_id = payment_object.get("id", "")

    metadata = payment_object.get("metadata", {}) or {}
    email = metadata.get("email", "")

    code = add_access_code(
        email=email,
        payment_id=payment_id,
    )

    return jsonify({
        "status": "success",
        "access_code": code,
        "payment_id": payment_id,
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
