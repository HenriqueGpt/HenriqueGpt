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

        # Tentativa de identificar o conteúdo da mensagem recebida
        if "text" in data and "message" in data["text"]:
            mensagem = data["text"]["message"]
            numero = data.get("phone")
        elif "image" in data and "caption" in data["image"]:
            mensagem = data["image"]["caption"]
            numero = data.get("phone")
        elif "message" in data:
            mensagem = data["message"]
            numero = data.get("phone")

        if not mensagem or not numero:
            print("❌ Dados incompletos.")
            return jsonify({"erro": "mensagem ou número ausente"}), 400

        openai_response = requests.post(
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

        resposta = openai_response.json()
        print("📦 Resposta da OpenAI:", resposta)

        # Verificação se a chave "choices" existe na resposta
        if "choices" not in resposta:
            erro = resposta.get("error", {})
            print("❌ Erro da OpenAI:", erro)
            return jsonify({"erro_openai": erro}), 500

        texto = resposta["choices"][0]["message"]["content"]

        envio = requests.post(
            f"https://api.z-api.io/instances/{os.environ['ZAPI_INSTANCE_ID']}/token/{os.environ['ZAPI_TOKEN']}/send-text",
            headers={"Content-Type": "application/json"},
            json={"phone": numero, "message": texto}
        )

        envio.raise_for_status()
        print("✅ Mensagem enviada com sucesso!")
        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ ERRO GERAL:")
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
