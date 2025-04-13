from flask import Flask, request
import requests
import os
from openai import OpenAI

app = Flask(__name__)

# Carregar variáveis de ambiente do Render
openai_api_key = os.environ.get("OPENAI_API_KEY")
zapi_instance_id = os.environ.get("ZAPI_INSTANCE_ID")
zapi_token = os.environ.get("ZAPI_TOKEN")

client = OpenAI(api_key=openai_api_key)

@app.route("/")
def home():
    return "HenriqueGPT na nuvem! ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        dados = request.json
        print("📥 Dados recebidos:", dados)

        # Verifica se a mensagem recebida é de texto
        texto_recebido = None

        if dados.get("text"):
            texto_recebido = dados["text"]["body"]

        elif dados.get("image"):
            caption = dados["image"].get("caption")
            texto_recebido = caption if caption else "(imagem sem legenda)"

        if not texto_recebido:
            print("❌ Mensagem não suportada ou vazia.")
            return "", 200

        # Enviar pergunta para o ChatGPT
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": texto_recebido}
            ]
        )

        texto = resposta.choices[0].message.content
        telefone = dados.get("phone")

        # Enviar a resposta ao WhatsApp pela Z-API (v2)
        url = f"https://api.z-api.io/instance/{zapi_instance_id}/send-text"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {zapi_token}"
        }

        payload = {
            "phone": telefone,
            "message": texto
        }

        envio = requests.post(url, headers=headers, json=payload)
        envio.raise_for_status()

        print("✅ Resposta enviada com sucesso.")
        return "", 200

    except Exception as e:
        print("❌ Erro:", e)
        return "", 500
