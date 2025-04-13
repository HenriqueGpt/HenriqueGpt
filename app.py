from flask import Flask, request, jsonify
import requests
import os
import traceback

app = Flask(__name__)

@app.route("/")
def home():
    return "HenriqueGPT na nuvem! ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("📥 Dados recebidos:", data)

        mensagem = None
        numero = None

        # 1. Mensagem de texto tradicional
        if "text" in data and "message" in data["text"]:
            mensagem = data["text"]["message"]
            numero = data.get("phone")

        # 2. Imagem com legenda
        elif "image" in data and "caption" in data["image"]:
            mensagem = data["image"]["caption"]
            numero = data.get("phone")

        # 3. Mensagem direta (sem estrutura text/image)
        elif "message" in data:
            mensagem = data["message"]
            numero = data.get("phone")

        if not mensagem or not numero:
            print("❌ Dados incompletos recebidos.")
            return jsonify({"erro": "mensagem ou número ausente"}), 400

        resposta = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
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
            f"https://api.z-api.io/instances/{os.environ['ZAPI_INSTANCE_ID']}/token/{os.environ['ZAPI_TOKEN']}/send-text",
            headers={"Content-Type": "application/json"},
            json={"phone": numero, "message": texto}
        )

        envio.raise_for_status()
        print("✅ Mensagem enviada com sucesso!")
        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ Erro no webhook:")
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
