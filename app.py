from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configurações das APIs
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
        data = request.json
        print("📥 Dados recebidos no webhook:", data)

        # Tenta extrair o número e a mensagem com segurança
        numero = data.get("phone")
        mensagem = data.get("text", {}).get("message")

        # Se não encontrar, imprime tudo para análise e retorna erro amigável
        if not numero or not mensagem:
            print("❗ Estrutura inesperada. Conteúdo recebido:", data)
            return jsonify({
                "erro": "Número ou mensagem ausente no JSON",
                "formato_esperado": {
                    "phone": "553199999999",
                    "text": {"message": "Olá"}
                }
            }), 400

        # Envia pergunta para o ChatGPT
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

        # Envia a resposta para o número pelo Z-API
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
