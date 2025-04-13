import os
import traceback
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
        print("📥 DADOS RECEBIDOS RAW:", request.data.decode())
        dados = request.get_json()
        print("📥 JSON:", dados)

        # Ignora mensagens de grupo
        if dados.get("isGroup", False):
            print("📛 Ignorado: mensagem de grupo.")
            return jsonify({"status": "ignorado (grupo)"}), 200

        numero = dados.get("phone")
        mensagem = dados.get("message")
        caption = dados.get("image", {}).get("caption", "")
        conteudo = caption if caption else mensagem

        if not numero or not conteudo:
            print("⚠️ Dados incompletos.")
            return jsonify({"erro": "mensagem ou número ausente"}), 400

        # Chamada OpenAI
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil e direto da Hydrotech Brasil."},
                {"role": "user", "content": conteudo}
            ]
        )

        texto = resposta['choices'][0]['message']['content']
        print("🤖 RESPOSTA:", texto)

        # Envio via Z-API
        zapi_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/v2/send-message"
        payload = {
            "phone": numero,
            "message": {"text": texto}
        }

        envio = requests.post(zapi_url, json=payload)
        envio.raise_for_status()

        print("✅ Mensagem enviada via Z-API")
        return jsonify({"resposta": texto}), 200

    except Exception as e:
        print("❌ ERRO INTERNO:", e)
        traceback.print_exc()  # LOGA o erro real no console da Render
        return jsonify({"erro": "erro interno no servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
