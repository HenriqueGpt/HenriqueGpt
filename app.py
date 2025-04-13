import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

# Chaves
openai.api_key = os.getenv("OPENAI_API_KEY")
zapi_instance_id = os.getenv("ZAPI_INSTANCE_ID")
zapi_token = os.getenv("ZAPI_TOKEN")

client = OpenAI()

@app.route("/")
def home():
    return "HenriqueGPT na nuvem! ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("📥 Dados recebidos:", json.dumps(data, indent=2, ensure_ascii=False))

        mensagem = extrair_mensagem(data)
        if not mensagem:
            print("⚠️ Mensagem vazia ou inválida.")
            return jsonify({"status": "ignorado"}), 200

        print("✉️ Pergunta recebida:", mensagem)

        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil e objetivo."},
                {"role": "user", "content": mensagem}
            ]
        )

        texto = resposta.choices[0].message.content.strip()
        print("🤖 Resposta gerada:", texto)

        numero = extrair_numero(data)
        enviar_resposta_zapi(zapi_instance_id, zapi_token, numero, texto)

        return jsonify({"status": "enviado"}), 200

    except Exception as e:
        print("❌ ERRO GERAL:")
        print(e)
        return jsonify({"status": "erro", "detalhes": str(e)}), 500

def extrair_mensagem(dados):
    try:
        if dados.get("text"):
            return dados["text"]["body"]
        elif dados.get("image") and dados["image"].get("caption"):
            return dados["image"]["caption"]
        elif dados.get("message"):
            return dados["message"]
        else:
            return None
    except Exception as e:
        print("❌ Erro ao extrair mensagem:", e)
        return None

def extrair_numero(dados):
    try:
        if "phone" in dados:
            return dados["phone"]
        elif "from" in dados:
            return dados["from"]
        return "numero_desconhecido"
    except Exception as e:
        print("❌ Erro ao extrair número:", e)
        return "erro"

def enviar_resposta_zapi(instance_id, token, telefone, resposta):
    url = f"https://api.z-api.io/instances/{instance_id}/send-text"
    headers = {
        "Content-Type": "application/json",
        "apikey": token
    }
    payload = {
        "phone": telefone,
        "message": resposta
    }

    envio = requests.post(url, json=payload, headers=headers)
    envio.raise_for_status()
    print("✅ Resposta enviada com sucesso.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
