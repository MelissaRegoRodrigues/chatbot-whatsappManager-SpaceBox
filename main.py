import re
from flask import Flask, request, Response
import requests
import os
from dotenv import load_dotenv
import random
import string
from database import upsert_auth_code, get_db_connection

load_dotenv()

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def verify_or_home():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token and challenge:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook verificado com sucesso!")
            return Response(challenge, status=200)
        else:
            print("Falha na verificação do webhook.")
            return Response("Unauthorized", status=403)

    return "Chatbot WhatsApp Flask rodando com sucesso!", 200

@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.get_json()
    phone_number = data.get("phone_number")
    auth_code = data.get("auth_code")

    if not phone_number:
        return "Missing phone_number", 400
    
    phone_number = clean_phone_number(phone_number)

    conn = get_db_connection()
    cur = conn.cursor()
    upsert_auth_code(phone_number, auth_code)
    conn.commit()
    cur.close()
    conn.close()

    response = send_message(phone_number, f"Seu código de autorização é: {auth_code}")

    return (response.text, response.status_code, {'Content-Type': 'application/json'})

@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    phone_number = data.get("phone_number")
    code = data.get("code")

    if not phone_number or not code:
        return "Missing phone_number or code", 400

    phone_number = clean_phone_number(phone_number)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT code FROM auth_codes WHERE phone_number = %s", (phone_number,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result and result[0] == code:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM auth_codes WHERE phone_number = %s", (phone_number,))
        conn.commit()
        cur.close()
        conn.close()
        return "Authorization successful", 200
    else:
        return "Invalid authorization code", 400

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Mensagem recebida:", data)

    try:
        entry = data["entry"][0]
        message = entry["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        msg_body = message["text"]["body"]

        reply = f"Você disse: {msg_body}"

        send_message(from_number, reply)

    except Exception as e:
        print("Erro:", e)

    return "OK", 200


def send_message(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    r = requests.post(url, json=payload, headers=headers)
    print("Resposta:", r.status_code, r.text)
    return r

def clean_phone_number(number):
    return re.sub(r'\D', '', number)  # Remove tudo que não for dígito

if __name__ == "__main__":
    app.run(port=5000)
