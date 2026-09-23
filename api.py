"""
api.py
Fitur pengayaan: REST API untuk enkripsi/dekripsi, diamankan JWT HMAC-SHA512
"""

import os
import hmac
import jwt
import datetime
from flask import Flask, request, jsonify
from crypto_utils import encrypt_text, decrypt_text

app = Flask(__name__)

# SECRET_KEY WAJIB diset lewat environment variable JWT_SECRET_KEY.
# Tidak ada nilai default di kode sumber (sesuai ketentuan tugas: kunci
# tidak boleh ditulis langsung di kode sumber maupun diunggah ke GitHub).
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY belum diset sebagai environment variable.\n"
        "Windows CMD  : set JWT_SECRET_KEY=<kunci_acak_minimal_64_byte>\n"
        "PowerShell   : $env:JWT_SECRET_KEY=\"<kunci_acak_minimal_64_byte>\""
    )

# Daftar pengguna diambil dari environment variable APP_USERS,
# format: "username1:password1,username2:password2"
# WAJIB diset, tidak ada kredensial tertanam di kode sumber.
_raw_users = os.environ.get("APP_USERS", "")
if not _raw_users:
    raise RuntimeError(
        "APP_USERS belum diset sebagai environment variable.\n"
        'Contoh (Windows CMD): set APP_USERS=agnia:passwordAgnia123,bunga:passwordBunga456'
    )

USERS = {}
for _pair in _raw_users.split(","):
    if ":" in _pair:
        _uname, _pwd = _pair.split(":", 1)
        USERS[_uname.strip()] = _pwd.strip()


def verify_credentials(username, password):
    """Cek username & password. Pakai compare_digest agar tahan timing attack."""
    if username not in USERS:
        return False
    return hmac.compare_digest(USERS[username], password)


def generate_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
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
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username dan password wajib diisi"}), 400
    if not verify_credentials(username, password):
        return jsonify({"error": "username atau password salah"}), 401
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