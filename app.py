import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Carregar variáveis de ambiente (.env ou configuradas no Render)
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "HenriqueGPT na nuvem! ✅"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("📥 Dados recebidos:", data)

        # --- TRATAMENTO DOS DADOS DA Z-API ---
        mensagem = ""
        numero = ""
        
        if 'message' in data:
            if 'text' in data['message']:
                mensagem = data['message']['text']
            elif 'image' in data['message'] and 'caption' in data['message']['image']:
                mensagem = data['message']['image']['caption']
            else:
                mensagem = "[mensagem não reconhecida]"

        if 'phone' in data:
            numero = data['phone']
        elif 'message' in data and 'phone' in data['message']:
            numero = data['message']['phone']

        if not mensagem or not numero:
            print("⚠️ Mensagem ou número não encontrado.")
            return jsonify({"status": "ignored"}), 400

        # --- ENVIAR PARA O CHATGPT ---
        openai_api_key = os.environ["OPENAI_API_KEY"]
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Você é um assistente da Hydrotech Brasil."},
                {"role": "user", "content": mensagem}
            ]
        }

        resposta = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
        resposta.raise_for_status()
        texto = resposta.json()["choices"][0]["message"]["content"]

        print("🤖 Resposta do ChatGPT:", texto)

        # --- ENVIAR PARA O WHATSAPP VIA Z-API ---
        url = f"https://api.z-api.io/instances/{os.environ['ZAPI_INSTANCE_ID']}/send-text"
        zapi_headers = {
            "Content-Type": "application/json",
            "Authorization": os.environ["ZAPI_TOKEN"]
        }
        payload = {
            "phone": numero,
            "message": texto
        }

        envio = requests.post(url, json=payload, headers=zapi_headers)
        envio.raise_for_status()
        print("✅ Enviado para o WhatsApp com sucesso!")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Erro no webhook:", str(e))
        return jsonify({"error": str(e)}), 500

# Iniciar o servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
