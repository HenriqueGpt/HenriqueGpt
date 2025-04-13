from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔐 Suas chaves (use variáveis de ambiente no futuro para segurança)
OPENAI_API_KEY = "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"
ZAPI_INSTANCE_ID = "3DFA1FF90F752079A4A8FA8592F99CB9"
ZAPI_TOKEN = "140585B259646B43AD0A4618"
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

@app.route("/")
def home():
    return "HenriqueGPT na nuvem! ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("📥 Dados recebidos no webhook:", data)

        # Verificação se veio JSON válido
        if not data:
            print("❌ JSON inválido ou ausente.")
            return jsonify({"erro": "JSON inválido ou ausente"}), 400

        # Tentativa de extração segura
        mensagem = data.get("text", {}).get("message", "")
        numero = data.get("phone", "")

        if not mensagem or not numero:
            print("❌ Mensagem ou número ausente.")
            return jsonify({"erro": "mensagem ou número ausente"}), 400

        print(f"📨 Mensagem recebida: {mensagem}")
        print(f"📱 Número: {numero}")

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
            print("❌ Erro da API OpenAI:", resposta.text)
            return jsonify({"erro": "Erro ao consultar o ChatGPT"}), 500

        texto = resposta.json()["choices"][0]["message"]["content"]
        print(f"🤖 Resposta gerada: {texto}")

        # Enviando resposta via Z-API
        envio = requests.post(
            ZAPI_URL,
            headers={"Content-Type": "application/json"},
            json={"phone": numero, "message": texto}
        )

        if envio.status_code != 200:
            print("❌ Falha ao enviar via Z-API:", envio.text)
            return jsonify({"erro": "Falha ao enviar mensagem"}), 500

        print("✅ Mensagem enviada com sucesso via WhatsApp!")
        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ Erro inesperado:", str(e))
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
