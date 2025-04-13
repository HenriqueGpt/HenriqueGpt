import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Variáveis de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
TOKEN = os.getenv("ZAPI_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/")
def home():
    return "HenriqueGPT está online."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        dados = request.json
        print("📥 Dados recebidos:", dados)

        numero = dados.get("phone")
        nome = dados.get("senderName")
        pergunta = dados.get("message")

        if not pergunta:
            return jsonify({"erro": "Dados incompletos"}), 400

        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": pergunta}
            ]
        )

        texto = resposta.choices[0].message.content
        print("🤖 Resposta:", texto)

        # Envio pela Z-API (corrigido)
        url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/v2/send-message"
        payload = {
            "phone": numero,
            "message": {
                "text": texto
            }
        }

        envio = requests.post(url, json=payload)
        envio.raise_for_status()

        return jsonify({"status": "Mensagem enviada com sucesso"}), 200

    except Exception as e:
        print("❌ ERRO GERAL:")
        print(e)
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run()
