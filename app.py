from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Variáveis de ambiente
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

        # CAPTION OU TEXTO
        mensagem = ""
        if "text" in data and "message" in data["text"]:
            mensagem = data["text"]["message"]
        elif "image" in data and "caption" in data["image"]:
            mensagem = data["image"]["caption"]
        else:
            print("⚠️ Dados incompletos recebidos")
            return jsonify({"erro": "mensagem ou caption não encontrada"}), 400

        numero = data.get("phone")
        if not mensagem or not numero:
            return jsonify({"erro": "mensagem ou número ausente"}), 400

        # 🔮 Enviando pergunta ao ChatGPT
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
        print("🤖 Resposta gerada:", texto)

        # ✅ Enviando resposta via Z-API
        envio = requests.post(
            ZAPI_URL,
            headers={"Content-Type": "application/json"},
            json={"phone": numero, "message": texto}
        )

        envio.raise_for_status()
        print("✅ Mensagem enviada com sucesso!")
        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ Erro:", e)
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
