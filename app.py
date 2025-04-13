from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OPENAI_API_KEY = "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"
ZAPI_INSTANCE_ID = "3DFA1FF90F752079A4A8FA8592F99CB9"
ZAPI_TOKEN = "140585B259646B43AD0A4618"
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

@app.route("/")
def home():
    return "HenriqueGPT está online!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("📥 Dados recebidos:", data)

        mensagem = data.get("text", {}).get("message")
        numero = data.get("phone")

        if not mensagem or not numero:
            return jsonify({"erro": "mensagem ou número ausente"}), 400

        print(f"✅ Mensagem de {numero}: {mensagem}")

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

        envio = requests.post(
            ZAPI_URL,
            headers={"Content-Type": "application/json"},
            json={"phone": numero, "message": texto}
        )

        envio.raise_for_status()
        print("✅ Enviado com sucesso!")
        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ Erro:", e)
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)