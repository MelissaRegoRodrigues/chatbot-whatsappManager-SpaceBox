from flask import Flask, request, Response
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Chatbot WhatsApp Flask rodando com sucesso!", 200

def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verificado com sucesso!")
        return Response(challenge, status=200)
    else:
        print("Falha na verificação do webhook.")
        return Response("Unauthorized", status=403)

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
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    r = requests.post(url, json=payload, headers=headers)
    print("Resposta:", r.status_code, r.text)

if __name__ == "__main__":
    app.run(port=5000)
