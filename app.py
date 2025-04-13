from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Carrega as variáveis de ambiente definidas no Render
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")

ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

@app.route("/")
def home():
    return "HenriqueGPT na nuvem! ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("📥 Dados recebidos:", data)

        # Extrai número
        numero = data.get("phone")

        # Pega texto de mensagem ou legenda da imagem
        mensagem = None
        if "text" in data:
            mensagem = data["text"].get("message")
        elif "image" in data:
            mensagem = data["image"].get("caption", "")
        else:
            mensagem = None

        if not mensagem or not numero:
            print("⚠️ Mensagem ou número ausente.")
            return jsonify({"erro": "mensagem ou número ausente"}), 400

        # Requisição para OpenAI
        resposta = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": mensagem}]
            }
        )

        texto = resposta.json()["choices"][0]["message"]["content"]
        print(f"🤖 Resposta gerada: {texto}")

        # Envia resposta via Z-API
        envio = requests.post(
            ZAPI_URL,
            headers={"Content-Type": "application/json"},
            json={"phone": numero, "message": texto}
        )

        envio.raise_for_status()
        print("✅ Mensagem enviada com sucesso!")
        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ Erro ao processar webhook:", str(e))
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
