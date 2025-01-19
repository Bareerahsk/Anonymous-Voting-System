from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import ring2

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/generate_signature', methods=['POST'])
def generate_signature():
    data = request.json
    message = data['message']
    num_keys = int(data['num_keys'])
    signer_index = int(data['signer_index'])

    # Generate key pairs
    private_keys = []
    public_keys = []
    for i in range(num_keys):
        private_key, public_key = ring2.generate_key_pair(seed=i)
        private_keys.append(private_key)
        public_keys.append(public_key)

    # Sign the message
    signature = ring2.sign(message, private_keys[signer_index], public_keys, signer_index)

    # Verify the signature
    is_valid = ring2.verify(message, signature, public_keys)

    return jsonify({
        'message': message,
        'signature': str(signature),
        'is_valid': is_valid
    })

if __name__ == '__main__':
    app.run(debug=True)
