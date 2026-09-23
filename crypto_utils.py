import os
import base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.exceptions import InvalidTag


def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key = kdf.derive(password.encode())
    return key, salt


def encrypt_text(plaintext: str, password: str) -> str:
    key, salt = derive_key(password)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    combined = salt + nonce + ciphertext
    return base64.b64encode(combined).decode()


def decrypt_text(encoded_data: str, password: str) -> str:
    combined = base64.b64decode(encoded_data)
    salt = combined[:16]
    nonce = combined[16:28]
    ciphertext = combined[28:]
    key, _ = derive_key(password, salt)
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
    except InvalidTag:
        raise ValueError("Dekripsi gagal: password salah atau data telah diubah.")


def encrypt_text_chacha(plaintext: str, password: str) -> str:
    key, salt = derive_key(password)
    nonce = os.urandom(12)
    chacha = ChaCha20Poly1305(key)
    ciphertext = chacha.encrypt(nonce, plaintext.encode(), None)
    combined = salt + nonce + ciphertext
    return base64.b64encode(combined).decode()


def decrypt_text_chacha(encoded_data: str, password: str) -> str:
    combined = base64.b64decode(encoded_data)
    salt = combined[:16]
    nonce = combined[16:28]
    ciphertext = combined[28:]
    key, _ = derive_key(password, salt)
    chacha = ChaCha20Poly1305(key)
    try:
        plaintext = chacha.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
    except InvalidTag:
        raise ValueError("Dekripsi gagal: password salah atau data telah diubah.")


def encrypt_file(input_path: str, output_path: str, password: str, algorithm: str = "aes"):
    with open(input_path, "rb") as f:
        data = f.read()
    key, salt = derive_key(password)
    nonce = os.urandom(12)
    if algorithm == "aes":
        cipher = AESGCM(key)
    elif algorithm == "chacha":
        cipher = ChaCha20Poly1305(key)
    else:
        raise ValueError("algorithm harus 'aes' atau 'chacha'")
    ciphertext = cipher.encrypt(nonce, data, None)
    combined = salt + nonce + ciphertext
    with open(output_path, "wb") as f:
        f.write(combined)


def decrypt_file(input_path: str, output_path: str, password: str, algorithm: str = "aes"):
    with open(input_path, "rb") as f:
        combined = f.read()
    salt = combined[:16]
    nonce = combined[16:28]
    ciphertext = combined[28:]
    key, _ = derive_key(password, salt)
    if algorithm == "aes":
        cipher = AESGCM(key)
    elif algorithm == "chacha":
        cipher = ChaCha20Poly1305(key)
    else:
        raise ValueError("algorithm harus 'aes' atau 'chacha'")
    try:
        plaintext = cipher.decrypt(nonce, ciphertext, None)
    except InvalidTag:
        raise ValueError("Dekripsi gagal: password salah atau file telah diubah.")
    with open(output_path, "wb") as f:
        f.write(plaintext)
