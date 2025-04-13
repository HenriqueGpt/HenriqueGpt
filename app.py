from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = "sk-proj-..."  # substitua aqui pela sua chave real
ZAPI_INSTANCE_ID = "3DFA1FF90F752079A4A8FA8592F99CB9"
ZAPI_TOKEN = "140585B259646B43AD0A4618"
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

@app.route("/")
def home():
    return "HenriqueGPT na nuvem! ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("📥 Dados recebidos:", data)

        if not data or "text" not in data or "phone" not in data:
            print("❌ Dados incompletos recebidos")
            return jsonify({"erro": "dados incompletos"}), 400

        mensagem = data["text"].get("message")
        numero = data.get("phone")

        if not mensagem or not numero:
            print("❌ Mensagem ou número ausente")
            return jsonify({"erro": "mensagem ou número ausente"}), 400

        # Chamada à OpenAI
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

        if resposta.status_code != 200:
            print("❌ Erro na resposta da OpenAI:", resposta.text)
            return jsonify({"erro": "Erro ao consultar OpenAI"}), 500

        texto = resposta.json()["choices"][0]["message"]["content"]
        print("🤖 Resposta gerada:", texto)

        # Envio pelo Z-API
        envio = requests.post(
            ZAPI_URL,
            headers={"Content-Type": "application/json"},
            json={"phone": numero, "message": texto}
        )

        if envio.status_code != 200:
            print("❌ Erro ao enviar mensagem pelo ZAPI:", envio.text)
            return jsonify({"erro": "Erro ao enviar mensagem"}), 500

        print("✅ Mensagem enviada com sucesso!")
        return jsonify({"resposta": texto}), 200

    except Exception as e:
        print("❌ Erro geral:", str(e))
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
