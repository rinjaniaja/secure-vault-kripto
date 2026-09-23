import os
import base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.exceptions import InvalidTag


def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Menurunkan kunci 256-bit dari password menggunakan scrypt.
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    key = kdf.derive(password.encode())
    return key, salt


def encrypt_text(plaintext: str, password: str) -> str:
    """
    Enkripsi teks memakai AES-256-GCM.
    Kunci diturunkan dari password. Salt dan nonce dibangkitkan acak.
    Hasil dikemas jadi satu string Base64: salt + nonce + ciphertext(+tag)
    """
    key, salt = derive_key(password)
    nonce = os.urandom(12)  # nonce 12 byte, standar untuk GCM

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

    combined = salt + nonce + ciphertext
    return base64.b64encode(combined).decode()


def decrypt_text(encoded_data: str, password: str) -> str:
    """
    Dekripsi teks hasil dari encrypt_text().
    Akan melempar error jika password salah atau data sudah diubah.
    """
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
    """
    Enkripsi teks memakai ChaCha20-Poly1305 (pembanding AES-GCM).
    """
    key, salt = derive_key(password)
    nonce = os.urandom(12)

    chacha = ChaCha20Poly1305(key)
    ciphertext = chacha.encrypt(nonce, plaintext.encode(), None)

    combined = salt + nonce + ciphertext
    return base64.b64encode(combined).decode()


def decrypt_text_chacha(encoded_data: str, password: str) -> str:
    """
    Dekripsi teks hasil dari encrypt_text_chacha().
    """
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


# --- Tes cepat ---
if __name__ == "__main__":
    password = "passwordku123"
    pesan_asli = "Ini pesan rahasia yang harus dienkripsi."

    print("=== TES 1: Enkripsi & Dekripsi normal (AES-256-GCM) ===")
    hasil_enkripsi = encrypt_text(pesan_asli, password)
    print("Ciphertext (Base64):", hasil_enkripsi)

    hasil_dekripsi = decrypt_text(hasil_enkripsi, password)
    print("Hasil dekripsi     :", hasil_dekripsi)
    print("Sesuai pesan asli? :", hasil_dekripsi == pesan_asli)

    print("\n=== TES 2: Dekripsi dengan password SALAH ===")
    try:
        decrypt_text(hasil_enkripsi, "password_salah")
        print("BAHAYA: seharusnya gagal tapi malah berhasil!")
    except ValueError as e:
        print("Berhasil ditolak, pesan error:", e)

    print("\n=== TES 3: Enkripsi & Dekripsi pakai ChaCha20-Poly1305 ===")
    hasil_enkripsi_chacha = encrypt_text_chacha(pesan_asli, password)
    print("Ciphertext (Base64):", hasil_enkripsi_chacha)

    hasil_dekripsi_chacha = decrypt_text_chacha(hasil_enkripsi_chacha, password)
    print("Hasil dekripsi     :", hasil_dekripsi_chacha)
    print("Sesuai pesan asli? :", hasil_dekripsi_chacha == pesan_asli)