from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)
API_BASE = "http://localhost:8000"  # Assuming FastAPI runs locally

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/generate_keys', methods=['GET'])
def generate_keys():
    response = requests.get(f"{API_BASE}/generate_keys")
    return jsonify(response.json())

@app.route('/sign', methods=['POST'])
def sign_message():
    # Forward the file and form data
    files = {'private_key': request.files['private_key']}
    data = {'message': request.form['message']}
    response = requests.post(f"{API_BASE}/sign", files=files, data=data)
    return jsonify(response.json())

@app.route('/verify', methods=['POST'])
def verify_signature():
    data = request.json
    response = requests.post(f"{API_BASE}/verify", json=data)
    return jsonify(response.json())

@app.route('/aes_encrypt', methods=['POST'])
def encrypt_data():
    data = request.json
    response = requests.post(f"{API_BASE}/aes_encrypt", json=data)
    return jsonify(response.json())

@app.route('/aes_decrypt', methods=['POST'])
def decrypt_data():
    data = request.json
    response = requests.post(f"{API_BASE}/aes_decrypt", json=data)
    return jsonify(response.json())

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Create a style.css file if it doesn't exist
    if not os.path.exists('static/style.css'):
        with open('static/style.css', 'w') as f:
            f.write('/* Default empty stylesheet */')
    
    # Create script.js if it doesn't exist
    if not os.path.exists('static/script.js'):
        with open('static/script.js', 'w') as f:
            f.write('// Default empty script')
    
    app.run(host='0.0.0.0', port=8080, debug=True)