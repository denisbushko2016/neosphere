import os
import json
import uuid
import base64
from datetime import datetime, timedelta

import requests
from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials


app = Flask(__name__)


# =====================================================
# CONFIG
# =====================================================

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

YOOKASSA_SHOP_ID = os.environ.get("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY")
RETURN_URL = os.environ.get("RETURN_URL", "https://neosphere.streamlit.app/")

ACCESS_DAYS = 30
PRICE_VALUE = "550.00"
PRICE_CURRENCY = "RUB"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# =====================================================
# GOOGLE SHEETS
# =====================================================

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


def ensure_headers():
    sheet = get_sheet()
    values = sheet.get_all_values()

    headers = [
        "email",
        "status",
        "activated_at",
        "expires_at",
        "payment_id",
        "created_at",
    ]

    if not values:
        sheet.append_row(headers)
        return headers

    current_headers = values[0]

    if current_headers != headers:
        sheet.update("A1:F1", [headers])

    return headers


def load_users():
    ensure_headers()
    sheet = get_sheet()
    records = sheet.get_all_records()
    return records


def activate_email_access(email, payment_id=""):
    if not email:
        raise RuntimeError("Email is missing")

    email = email.strip().lower()

    sheet = get_sheet()
    ensure_headers()

    values = sheet.get_all_values()
    headers = values[0]

    today = datetime.now().date()
    activated_at = today.isoformat()
    expires_at = (today + timedelta(days=ACCESS_DAYS)).isoformat()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    existing_row_number = None

    for index, row_values in enumerate(values[1:], start=2):
        row_email = row_values[0].strip().lower() if len(row_values) > 0 else ""

        if row_email == email:
            existing_row_number = index
            break

    row = [
        email,
        "active",
        activated_at,
        expires_at,
        payment_id,
        created_at,
    ]

    if existing_row_number:
        sheet.update(f"A{existing_row_number}:F{existing_row_number}", [row])
    else:
        sheet.append_row(row)

    return {
        "email": email,
        "status": "active",
        "activated_at": activated_at,
        "expires_at": expires_at,
        "payment_id": payment_id,
    }


# =====================================================
# YOOKASSA PAYMENT CREATION
# =====================================================

def create_yookassa_payment(email=""):
    if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
        raise RuntimeError("YOOKASSA_SHOP_ID or YOOKASSA_SECRET_KEY is missing")

    email = email.strip().lower()

    if not email:
        raise RuntimeError("Email is required to create payment")

    url = "https://api.yookassa.ru/v3/payments"

    auth_string = f"{YOOKASSA_SHOP_ID}:{YOOKASSA_SECRET_KEY}"
    auth_header = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Idempotence-Key": str(uuid.uuid4()),
        "Content-Type": "application/json",
    }

    payload = {
        "amount": {
            "value": PRICE_VALUE,
            "currency": PRICE_CURRENCY,
        },
        "confirmation": {
            "type": "redirect",
            "return_url": RETURN_URL,
        },
        "capture": True,
        "description": "NeoSphere Access — доступ на 30 дней",
        "metadata": {
            "product": "neosphere_access_30_days",
            "email": email,
        },
        "receipt": {
            "customer": {
                "email": email,
            },
            "items": [
                {
                    "description": "NeoSphere Access — доступ на 30 дней",
                    "quantity": "1.00",
                    "amount": {
                        "value": PRICE_VALUE,
                        "currency": PRICE_CURRENCY,
                    },
                    "vat_code": 1,
                    "payment_subject": "service",
                    "payment_mode": "full_payment",
                }
            ],
        },
    }

    response = requests.post(url, headers=headers, json=payload, timeout=20)

    if response.status_code not in (200, 201):
        raise RuntimeError(f"YooKassa error: {response.status_code} {response.text}")

    data = response.json()

    return {
        "payment_id": data.get("id"),
        "confirmation_url": data["confirmation"]["confirmation_url"],
    }


# =====================================================
# ROUTES
# =====================================================

@app.route("/", methods=["GET"])
def home():
    return "NeoSphere payment server is running"


@app.route("/test-activate-email", methods=["GET"])
def test_activate_email():
    result = activate_email_access(
        email="denisbushko2016@gmail.com",
        payment_id="test_payment",
    )

    return jsonify({
        "status": "success",
        "result": result,
    }), 200


@app.route("/pay", methods=["GET"])
def pay_redirect():
    email = request.args.get("email", "").strip().lower()

    if not email:
        return "Email is required", 400

    payment = create_yookassa_payment(email=email)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0; url={payment['confirmation_url']}">
        <title>NeoSphere Payment</title>
    </head>
    <body style="background:#05070A;color:white;font-family:Arial;text-align:center;padding-top:80px;">
        <h2>Переход к оплате NeoSphere...</h2>
        <p>Если переход не произошёл автоматически, нажмите:</p>
        <a style="color:#8EB6FF;" href="{payment['confirmation_url']}">Перейти к оплате</a>
    </body>
    </html>
    """


@app.route("/create-payment", methods=["POST"])
def create_payment():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()

    payment = create_yookassa_payment(email=email)

    return jsonify({
        "status": "success",
        "payment_id": payment["payment_id"],
        "payment_url": payment["confirmation_url"],
    }), 200


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
        return jsonify({
            "status": "ignored",
            "event": event,
        }), 200

    payment_id = payment_object.get("id", "")

    metadata = payment_object.get("metadata", {}) or {}
    email = metadata.get("email", "").strip().lower()

    result = activate_email_access(
        email=email,
        payment_id=payment_id,
    )

    return jsonify({
        "status": "success",
        "result": result,
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)