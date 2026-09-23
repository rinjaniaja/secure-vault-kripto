"""Unit test untuk hybrid_crypto.py"""

import pytest
from hybrid_crypto import generate_rsa_keypair, encrypt_hybrid, decrypt_hybrid


def test_hybrid_encrypt_decrypt_success():
    """Enkripsi lalu dekripsi harus menghasilkan plaintext yang sama."""
    private_key, public_key = generate_rsa_keypair()
    plaintext = b"Pesan rahasia untuk hybrid encryption"

    result = encrypt_hybrid(plaintext, public_key)
    decrypted = decrypt_hybrid(
        result["ciphertext"], result["nonce"],
        result["encrypted_session_key"], private_key
    )

    assert decrypted == plaintext


def test_hybrid_decrypt_wrong_private_key_fails():
    """Dekripsi dengan private key yang salah harus gagal."""
    private_key1, public_key1 = generate_rsa_keypair()
    private_key2, _ = generate_rsa_keypair()  # keypair lain, tidak berpasangan

    plaintext = b"Data sensitif"
    result = encrypt_hybrid(plaintext, public_key1)

    with pytest.raises(Exception):
        decrypt_hybrid(
            result["ciphertext"], result["nonce"],
            result["encrypted_session_key"], private_key2
        )


def test_hybrid_tampered_ciphertext_fails():
    """Ciphertext yang diubah 1 byte harus gagal saat dekripsi (AEAD tag check)."""
    private_key, public_key = generate_rsa_keypair()
    plaintext = b"Data penting"
    result = encrypt_hybrid(plaintext, public_key)

    tampered = bytearray(result["ciphertext"])
    tampered[0] ^= 0xFF  # ubah 1 byte

    with pytest.raises(Exception):
        decrypt_hybrid(
            bytes(tampered), result["nonce"],
            result["encrypted_session_key"], private_key
        )