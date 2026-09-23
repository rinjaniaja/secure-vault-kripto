"""
api.py
Fitur pengayaan: REST API untuk enkripsi/dekripsi, diamankan JWT HMAC-SHA512
"""

import os
import jwt
import datetime
from flask import Flask, request, jsonify
from crypto_utils import encrypt_text, decrypt_text

app = Flask(__name__)
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "ganti-ini-lewat-environment-variable")


def generate_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS512")


def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS512"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token tidak ditemukan"}), 401
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        if payload is None:
            return jsonify({"error": "Token tidak valid atau kadaluarsa"}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"error": "username wajib diisi"}), 400
    token = generate_token(username)
    return jsonify({"token": token})


@app.route("/encrypt", methods=["POST"])
@require_auth
def encrypt_endpoint():
    data = request.json
    plaintext = data.get("plaintext")
    password = data.get("password")
    if not plaintext or not password:
        return jsonify({"error": "plaintext dan password wajib diisi"}), 400
    ciphertext = encrypt_text(plaintext, password)
    return jsonify({"ciphertext": ciphertext})


@app.route("/decrypt", methods=["POST"])
@require_auth
def decrypt_endpoint():
    data = request.json
    ciphertext = data.get("ciphertext")
    password = data.get("password")
    if not ciphertext or not password:
        return jsonify({"error": "ciphertext dan password wajib diisi"}), 400
    try:
        plaintext = decrypt_text(ciphertext, password)
        return jsonify({"plaintext": plaintext})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)