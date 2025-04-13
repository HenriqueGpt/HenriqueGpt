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

# Configura chave da OpenAI
openai.api_key = OPENAI_API_KEY

@app.route('/')
def home():
    return "HenriqueGPT online! ✅"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        raw_data = request.data.decode()
        print("📥 DADOS RECEBIDOS RAW:", raw_data)

        dados = request.get_json()
        print("📥 JSON:", dados)

        # Ignorar mensagens de grupo
        if dados.get("isGroup"):
            print("📛 Ignorado: mensagem de grupo.")
            return jsonify({"status": "ignorado"}), 200

        numero = dados.get("phone")
        mensagem = dados.get("text", {}).get("message", "")

        if not numero or not mensagem:
            print("⚠️ Dados incompletos.")
            return jsonify({"erro": "mensagem ou número ausente"}), 400

        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil e direto da Hydrotech Brasil."},
                {"role": "user", "content": mensagem}
            ]
        )

        texto = resposta['choices'][0]['message']['content']
        print("🤖 Resposta gerada:", texto)

        # Enviar de volta via Z-API
        zapi_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/v2/send-message"
        payload = {
            "phone": numero,
            "message": {
                "text": texto
            }
        }

        envio = requests.post(zapi_url, json=payload)
        print("📨 Resposta da Z-API:", envio.status_code, envio.text)
        envio.raise_for_status()

        print("✅ Enviado com sucesso via Z-API")
        return jsonify({"resposta": texto}), 200

    except Exception as e:
        print("❌ ERRO:", e)
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
