import os
import json
import uuid
import base64
import secrets
import string
from datetime import datetime
import smtplib
from email.message import EmailMessage

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

PRICE_VALUE = "550.00"
PRICE_CURRENCY = "RUB"
BREVO_SMTP_SERVER = os.environ.get("BREVO_SMTP_SERVER", "smtp-relay.brevo.com")
BREVO_SMTP_PORT = int(os.environ.get("BREVO_SMTP_PORT", "587"))
BREVO_SMTP_LOGIN = os.environ.get("BREVO_SMTP_LOGIN")
BREVO_SMTP_PASSWORD = os.environ.get("BREVO_SMTP_PASSWORD")
EMAIL_FROM = os.environ.get("EMAIL_FROM", BREVO_SMTP_LOGIN)

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


# =====================================================
# ACCESS CODE GENERATION
# =====================================================

def generate_code():
    alphabet = string.ascii_uppercase + string.digits
    part1 = "".join(secrets.choice(alphabet) for _ in range(4))
    part2 = "".join(secrets.choice(alphabet) for _ in range(4))
    return f"NS-{part1}-{part2}"


def add_access_code(email="", payment_id=""):
    sheet = get_sheet()

    records = sheet.get_all_records()
    existing_codes = [row.get("code") for row in records]

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
# =====================================================
# EMAIL DELIVERY
# =====================================================

def send_access_email(email, code):
    if not email:
        print("No email provided, skipping email delivery")
        return False

    if not BREVO_SMTP_LOGIN or not BREVO_SMTP_PASSWORD:
        raise RuntimeError("BREVO SMTP credentials are missing")

    msg = EmailMessage()
    msg["Subject"] = "Ваш код доступа NeoSphere"
    msg["From"] = EMAIL_FROM
    msg["To"] = email

    msg.set_content(
        f"""Здравствуйте!

Ваш код доступа NeoSphere:

{code}

Сайт для входа:
https://neosphere.streamlit.app/

Срок действия:
30 дней с момента первой активации.

Рекомендации:
— используйте наушники;
— не используйте сессии при управлении транспортом или техникой;
— при дискомфорте остановите сессию.

NeoSphere
"""
    )

    with smtplib.SMTP(BREVO_SMTP_SERVER, BREVO_SMTP_PORT) as server:
        server.starttls()
        server.login(BREVO_SMTP_LOGIN, BREVO_SMTP_PASSWORD)
        server.send_message(msg)

    return True


# =====================================================
# YOOKASSA PAYMENT CREATION
# =====================================================

def create_yookassa_payment(email=""):
    if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
        raise RuntimeError("YOOKASSA_SHOP_ID or YOOKASSA_SECRET_KEY is missing")

    url = "https://api.yookassa.ru/v3/payments"

    auth_string = f"{YOOKASSA_SHOP_ID}:{YOOKASSA_SECRET_KEY}"
    auth_header = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Idempotence-Key": str(uuid.uuid4()),
        "Content-Type": "application/json",
    }

    customer_email = email if email else "client@example.com"

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
        "description": "NeoSphere Access — цифровой доступ на 30 дней",
        "metadata": {
            "product": "neosphere_access_30_days",
            "email": customer_email,
        },
        "receipt": {
            "customer": {
                "email": customer_email,
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
    confirmation_url = data["confirmation"]["confirmation_url"]

    return {
        "payment_id": data.get("id"),
        "confirmation_url": confirmation_url,
    }


# =====================================================
# ROUTES
# =====================================================

@app.route("/", methods=["GET"])
def home():
    return "NeoSphere payment server is running"


@app.route("/test-create-key", methods=["GET"])

def test_create_key():

    test_email = "denisbushko2016@gmail.com"

    code = add_access_code(

        email=test_email,

        payment_id="test_payment",

    )

    email_sent = send_access_email(test_email, code)

    return jsonify({

        "status": "success",

        "access_code": code,

        "email_sent": email_sent,

    }), 200


@app.route("/create-payment", methods=["POST", "GET"])
def create_payment():
    email = ""

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        email = data.get("email", "").strip()

    payment = create_yookassa_payment(email=email)

    return jsonify({
        "status": "success",
        "payment_id": payment["payment_id"],
        "payment_url": payment["confirmation_url"],
    }), 200


@app.route("/pay", methods=["GET"])
def pay_redirect():
    email = request.args.get("email", "").strip()
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

email_sent = send_access_email(email, code)

return jsonify({
    "status": "success",
    "access_code": code,
    "payment_id": payment_id,
    "email_sent": email_sent,
}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
