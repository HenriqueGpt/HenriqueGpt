from flask import Flask, request, jsonify
import os
import requests
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 🔐 Chaves de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")
zapi_instance_id = os.getenv("ZAPI_INSTANCE_ID")
zapi_token = os.getenv("ZAPI_TOKEN")

@app.route("/", methods=["GET"])
def index():
    return "HenriqueGPT na nuvem! ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        dados = request.json
        print("📥 Dados recebidos:", dados)

        mensagem = None
        numero = None

        # 👀 Detecta formato de mensagem
        if "message" in dados and "text" in dados["message"]:
            mensagem = dados["message"]["text"]
            numero = dados["message"]["phone"]
        elif "text" in dados:
            mensagem = dados["text"]
            numero = dados["phone"]
        elif "image" in dados and "caption" in dados["image"]:
            mensagem = dados["image"]["caption"]
            numero = dados["phone"]
        else:
            print("⚠️ Dados incompletos ou não suportados")
            return jsonify({"status": "ignorado"}), 400

        print("📲 Mensagem:", mensagem)
        print("📞 Número:", numero)

        # 🧠 Envia para o ChatGPT
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado da Hydrotech Brasil."},
                {"role": "user", "content": mensagem}
            ]
        )

        texto = resposta.choices[0].message.content.strip()
        print("🤖 Resposta:", texto)

        # 🚀 Envia a resposta via Z-API (formato novo)
        url = f"https://api.z-api.io/instance/{zapi_instance_id}/send-text"
        headers = {
            "Authorization": f"Bearer {zapi_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "phone": numero,
            "message": texto
        }

        envio = requests.post(url, headers=headers, json=payload)
        envio.raise_for_status()
        print("📤 Resposta enviada com sucesso")

        return jsonify({"status": "enviado"}), 200

    except Exception as e:
        print("❌ Erro geral:", str(e))
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
