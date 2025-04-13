from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

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
        data = request.json
        print("📥 Dados recebidos:", data)

        # Tentativa de extrair número e mensagem considerando múltiplos formatos
        numero = (
            data.get("phone") or
            data.get("From") or
            data.get("from") or
            data.get("sender", {}).get("phone") or
            data.get("participantPhone")
        )

        mensagem = (
            data.get("text", {}).get("message") or
            data.get("message") or
            data.get("caption") or
            data.get("body")
        )

        if not numero or not mensagem:
            print("⚠️ Dados incompletos ou inválidos recebidos.")
            return jsonify({"erro": "Dados incompletos ou inválidos"}), 400

        # Chamada ao ChatGPT
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

        resposta.raise_for_status()
        texto = resposta.json()["choices"][0]["message"]["content"]
        print(f"🤖 Resposta gerada: {texto}")

        # Enviando de volta via Z-API
        envio = requests.post(
            ZAPI_URL,
            headers={"Content-Type": "application/json"},
            json={"phone": numero, "message": texto}
        )
        envio.raise_for_status()

        print("✅ Mensagem enviada com sucesso!")
        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ Erro geral no webhook:", str(e))
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
