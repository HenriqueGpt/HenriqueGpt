import os
import requests
import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Variáveis de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")

openai.api_key = OPENAI_API_KEY

@app.route('/')
def home():
    return "HenriqueGPT online! ✅"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json()
        print("📥 JSON recebido:", dados)

        if dados.get("isGroup"):
            print("⚠️ Mensagem ignorada (vinda de grupo)")
            return jsonify({"info": "Mensagem de grupo ignorada"}), 200

        numero = dados.get("phone")
        mensagem = dados.get("message", "")
        caption = dados.get("image", {}).get("caption", "")
        conteudo = caption or mensagem or "[Mensagem vazia]"

        if not numero:
            print("❌ Número ausente!")
            return jsonify({"erro": "Número ausente!"}), 400

        print(f"💬 Conteúdo recebido: {conteudo}")

        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil e direto da Hydrotech Brasil."},
                {"role": "user", "content": conteudo}
            ]
        )

        texto = resposta['choices'][0]['message']['content']
        print("🤖 Resposta:", texto)

        zapi_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/v2/send-message"
        payload = {
            "phone": numero,
            "message": {
                "text": texto
            }
        }

        envio = requests.post(zapi_url, json=payload)
        envio.raise_for_status()

        print("✅ Mensagem enviada com sucesso via Z-API")
        return jsonify({"resposta": texto}), 200

    except Exception as e:
        print("❌ ERRO GERAL:", e)
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
