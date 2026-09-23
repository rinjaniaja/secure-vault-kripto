"""
hybrid_crypto.py
Fitur pengayaan: Hybrid Encryption (RSA-OAEP + AES-256-GCM)
Session key AES dibungkus dengan RSA-OAEP agar bisa didistribusikan dengan aman.
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_rsa_keypair(key_size=2048):
    """Generate pasangan kunci RSA. Return (private_key, public_key)."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def encrypt_hybrid(plaintext: bytes, rsa_public_key):
    """
    Enkripsi plaintext dengan skema hybrid:
    1. Generate session key AES-256 acak
    2. Enkripsi plaintext dengan AES-256-GCM pakai session key
    3. Bungkus session key dengan RSA-OAEP pakai public key penerima

    Return dict: {ciphertext, nonce, encrypted_session_key}
    """
    session_key = os.urandom(32)  # AES-256 = 32 byte
    nonce = os.urandom(12)        # nonce standar untuk GCM

    aesgcm = AESGCM(session_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    encrypted_session_key = rsa_public_key.encrypt(
        session_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return {
        "ciphertext": ciphertext,
        "nonce": nonce,
        "encrypted_session_key": encrypted_session_key,
    }


def decrypt_hybrid(ciphertext: bytes, nonce: bytes, encrypted_session_key: bytes, rsa_private_key):
    """
    Dekripsi hasil encrypt_hybrid:
    1. Buka session key pakai RSA private key
    2. Dekripsi ciphertext dengan AES-GCM pakai session key hasil bongkar

    Akan raise exception kalau private key salah atau ciphertext diubah
    (verifikasi GCM authentication tag).
    """
    session_key = rsa_private_key.decrypt(
        encrypted_session_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    aesgcm = AESGCM(session_key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext