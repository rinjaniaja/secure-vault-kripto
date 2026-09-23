import os
import base64
import pytest
from crypto_utils import (
    derive_key,
    encrypt_text,
    decrypt_text,
    encrypt_text_chacha,
    decrypt_text_chacha,
    encrypt_file,
    decrypt_file,
)


def test_derive_key_same_salt():
    """Test 5: derive_key dengan salt sama menghasilkan key yang sama."""
    salt = os.urandom(16)
    password = "SecretPassword123!"
    key1, salt1 = derive_key(password, salt)
    key2, salt2 = derive_key(password, salt)
    assert key1 == key2
    assert salt1 == salt2 == salt


def test_derive_key_different_salt():
    """Test 6: derive_key dengan salt berbeda menghasilkan key yang berbeda."""
    password = "SecretPassword123!"
    salt1 = os.urandom(16)
    salt2 = os.urandom(16)
    key1, _ = derive_key(password, salt1)
    key2, _ = derive_key(password, salt2)
    assert key1 != key2


def test_aes_gcm_text_encrypt_decrypt():
    """Test 1: Enkripsi-dekripsi teks AES-GCM menghasilkan teks yang sama dengan aslinya."""
    plaintext = "Pesan Rahasia UTS Keamanan Informasi 2026 🔒"
    password = "MyStrongPassword456!"
    ciphertext_b64 = encrypt_text(plaintext, password)
    assert ciphertext_b64 != plaintext
    decrypted = decrypt_text(ciphertext_b64, password)
    assert decrypted == plaintext


def test_chacha20_poly1305_text_encrypt_decrypt():
    """Test 2: Enkripsi-dekripsi teks ChaCha20-Poly1305 menghasilkan teks yang sama."""
    plaintext = "Pesan Rahasia ChaCha20 Poly1305 ⚡"
    password = "MyStrongPassword789!"
    ciphertext_b64 = encrypt_text_chacha(plaintext, password)
    assert ciphertext_b64 != plaintext
    decrypted = decrypt_text_chacha(ciphertext_b64, password)
    assert decrypted == plaintext


def test_decrypt_wrong_password_raises_value_error():
    """Test 3: Dekripsi dengan password salah harus raise ValueError."""
    plaintext = "Data penting yang disembunyikan."
    correct_pass = "PasswordBenar123"
    wrong_pass = "PasswordSalah456"

    # Testing AES-GCM
    enc_aes = encrypt_text(plaintext, correct_pass)
    with pytest.raises(ValueError, match="password salah atau data telah diubah"):
        decrypt_text(enc_aes, wrong_pass)

    # Testing ChaCha20
    enc_chacha = encrypt_text_chacha(plaintext, correct_pass)
    with pytest.raises(ValueError, match="password salah atau data telah diubah"):
        decrypt_text_chacha(enc_chacha, wrong_pass)


def test_decrypt_tampered_ciphertext_raises_value_error():
    """Test 4: Dekripsi ciphertext yang diubah/rusak harus raise ValueError."""
    plaintext = "Data terotentikasi."
    password = "SecurePassword123"

    ciphertext_b64 = encrypt_text(plaintext, password)
    raw_data = bytearray(base64.b64decode(ciphertext_b64))
    # Ubah byte ciphertext di pertengahan
    raw_data[-5] ^= 0xFF
    tampered_b64 = base64.b64encode(raw_data).decode()

    with pytest.raises(ValueError):
        decrypt_text(tampered_b64, password)


def test_file_encrypt_decrypt_aes(tmp_path):
    """Test 7: Enkripsi-dekripsi file menghasilkan isi file yang identik dengan aslinya (tmp_path fixture)."""
    input_file = tmp_path / "original_document.pdf"
    encrypted_file = tmp_path / "document.pdf.enc"
    decrypted_file = tmp_path / "decrypted_document.pdf"

    original_content = b"Binary Content PDF Test Data \x00\x01\x02\xff\xfe\xfd" * 50
    input_file.write_bytes(original_content)

    password = "FilePassword123!"

    # Enkripsi file AES
    encrypt_file(str(input_file), str(encrypted_file), password, algorithm="aes")
    assert encrypted_file.exists()
    assert encrypted_file.read_bytes() != original_content

    # Dekripsi file AES
    decrypt_file(str(encrypted_file), str(decrypted_file), password, algorithm="aes")
    assert decrypted_file.exists()
    assert decrypted_file.read_bytes() == original_content


def test_file_encrypt_decrypt_chacha(tmp_path):
    """Test 8: Enkripsi file dengan algoritma 'chacha' juga bekerja dengan benar."""
    input_file = tmp_path / "image.png"
    encrypted_file = tmp_path / "image.png.enc"
    decrypted_file = tmp_path / "decrypted_image.png"

    original_content = b"PNG Image Mock Content \x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" * 40
    input_file.write_bytes(original_content)

    password = "ChaChaFilePass123!"

    # Enkripsi file ChaCha
    encrypt_file(str(input_file), str(encrypted_file), password, algorithm="chacha")
    assert encrypted_file.exists()
    assert encrypted_file.read_bytes() != original_content

    # Dekripsi file ChaCha
    decrypt_file(str(encrypted_file), str(decrypted_file), password, algorithm="chacha")
    assert decrypted_file.exists()
    assert decrypted_file.read_bytes() == original_content
