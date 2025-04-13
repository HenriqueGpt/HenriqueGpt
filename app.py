from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔐 Suas chaves e tokens
OPENAI_API_KEY = "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"
ZAPI_INSTANCE_ID = "3DFA1FF90F752079A4A8FA8592F99CB9"
ZAPI_TOKEN = "140585B259646B43AD0A4618"

# 📤 URL de envio da Z-API
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

# 🌐 Teste rápido no navegador
@app.route("/")
def home():
    return "HenriqueGPT na nuvem! ✅"

# 🔄 Webhook para processar mensagens
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("🔎 Content-Type recebido:", request.headers.get("Content-Type"))

        # Tenta carregar o JSON da requisição
        try:
            data = request.get_json(force=True)
        except Exception as e:
            print("❌ JSON inválido recebido:", e)
            return jsonify({"erro": "JSON inválido ou mal formatado", "detalhe": str(e)}), 400

        print("📥 Dados recebidos no webhook:", data)

        # Validação dos campos esperados
        numero = data.get("phone")
        mensagem = data.get("text", {}).get("message")

        if not numero or not mensagem:
            print("❗ Estrutura inesperada. Conteúdo:", data)
            return jsonify({
                "erro": "Número ou mensagem ausente no JSON",
                "formato_esperado": {
                    "phone": "553199999999",
                    "text": {"message": "Olá"}
                }
            }), 400

        # Chamada à API da OpenAI
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

        # Envio da resposta via Z-API
        envio = requests.post(
            ZAPI_URL,
            headers={"Content-Type": "application/json"},
            json={"phone": numero, "message": texto}
        )

        envio.raise_for_status()
        print("✅ Mensagem enviada com sucesso!")

        return jsonify({"resposta": texto})

    except Exception as e:
        print("❌ Erro no webhook:", e)
        return jsonify({"erro": str(e)}), 500

# 🚀 Start do servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
