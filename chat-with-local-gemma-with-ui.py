from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__, static_folder="static")

OLLAMA_API_URL = "http://localhost:11434/api/generate"

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/generate', methods=['POST'])
def proxy_to_ollama():
    try:
        user_input = request.get_json()
        payload = {
            "model": "gemma:2b",
            "prompt": user_input.get("prompt"),
            "stream": False
        }

        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        return (response.content, response.status_code, response.headers.items())

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to Ollama", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
