import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Menurunkan kunci 256-bit dari password menggunakan scrypt.
    Jika salt tidak diberikan, akan dibuat salt acak baru (untuk enkripsi baru).
    Jika salt diberikan, akan menghasilkan kunci yang sama (untuk dekripsi).
    
    Return: (key, salt)
    """
    if salt is None:
        salt = os.urandom(16)  # salt acak 16 byte, CSPRNG

    kdf = Scrypt(
        salt=salt,
        length=32,      # 32 byte = 256 bit, sesuai kebutuhan AES-256
        n=2**14,        # cost factor
        r=8,
        p=1,
    )
    key = kdf.derive(password.encode())
    return key, salt


# --- Bagian ini untuk tes cepat, jalankan file ini langsung ---
if __name__ == "__main__":
    password = "passwordku123"
    
    key1, salt1 = derive_key(password)
    print("Key pertama :", key1.hex())
    print("Salt        :", salt1.hex())
    
    # Coba turunkan lagi pakai salt yang sama -> harus hasilkan key yang SAMA
    key2, _ = derive_key(password, salt1)
    print("Key kedua   :", key2.hex())
    print("Key sama?   :", key1 == key2)