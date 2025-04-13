from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def index():
    return '🚀 HenriqueGPT rodando com Z-API!'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.json
        print("📥 Dados recebidos:", dados)

        mensagem = dados.get("message", "")
        numero = dados.get("phone", "")
        imagem = dados.get("image", {})
        caption = imagem.get("caption", "")

        if not numero:
            print("❌ Dados incompletos.")
            return jsonify({"erro": "Dados incompletos"}), 400

        conteudo = caption if caption else mensagem

        if not conteudo:
            print("⚠️ Mensagem ou legenda não identificada.")
            return jsonify({"erro": "Nada para responder."}), 400

        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                { "role": "user", "content": conteudo }
            ]
        )

        texto = resposta.choices[0].message.content
        print("✅ RESPOSTA GPT:", texto)

        # Envia resposta via Z-API
        zapi_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/send-text"
        headers = {
            "Authorization": f"Bearer {ZAPI_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "phone": numero,
            "message": texto
        }

        envio = requests.post(zapi_url, json=payload, headers=headers)
        envio.raise_for_status()

        return jsonify({"resposta": texto}), 200

    except Exception as e:
        print("❌ ERRO GERAL:", e)
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
