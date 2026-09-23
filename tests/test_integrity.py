"""
tests/test_integrity.py
=============================================================================
PERBAIKAN PENGUJIAN WAJIB
Tugas UTS Keamanan Informasi — Topik A: Aplikasi Enkripsi Modern
Dikerjakan oleh: Serli Nadia Azzahra

Menguji properti KEAMANAN inti dari skema AEAD (Authenticated Encryption
with Associated Data) yang dipakai crypto_utils.py, yaitu:
  1. Kerahasiaan bergantung penuh pada password yang benar.
  2. Integritas: perubahan sekecil apa pun pada ciphertext harus terdeteksi
     dan ditolak (lewat verifikasi authentication tag AEAD).
  3. Data biner non-teks (gambar & PDF) tetap identik bit-per-bit setelah
     proses enkripsi -> dekripsi (round-trip), dibuktikan dengan hash SHA-256.

Konsep "Authentication Tag AEAD" (dijelaskan singkat untuk sesi tanya jawab):
AES-256-GCM dan ChaCha20-Poly1305 adalah cipher AEAD: selain mengenkripsi
plaintext, keduanya juga menghasilkan sebuah "authentication tag" (16 byte)
yang berfungsi seperti checksum kriptografis atas ciphertext. Saat dekripsi,
tag ini dihitung ulang dan dibandingkan. Kalau satu byte saja dari
ciphertext (atau tag) berubah -- baik karena kerusakan data maupun karena
serangan aktif -- verifikasi tag akan gagal dan library melempar
`InvalidTag`, yang oleh crypto_utils.py ditangkap dan diubah jadi
`ValueError` yang lebih ramah pengguna. Ini mencegah "malleability
attack", yaitu skenario di mana penyerang mengubah ciphertext dengan
harapan menghasilkan plaintext lain yang masih "masuk akal" tanpa
mengetahui kunci -- pada mode non-AEAD (seperti CBC/ECB polos) ini bisa
lolos tanpa terdeteksi.
"""

import os
import hashlib
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crypto_utils import (
    encrypt_text, decrypt_text,
    encrypt_file, decrypt_file,
)

PASSWORD_BENAR = "PasswordUjiIntegritas123!"
PASSWORD_SALAH = "PasswordSalahTotal456!"


# =============================================================================
# HELPER: pembuat file citra & PDF minimal yang VALID (bukan sekadar
# random bytes dengan header palsu) untuk dipakai di beberapa test.
# =============================================================================
def _buat_png_valid_minimal() -> bytes:
    """Buat PNG 8x8 piksel yang benar-benar valid memakai Pillow."""
    from PIL import Image
    import io

    img = Image.new("RGB", (8, 8), color=(120, 40, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _buat_pdf_valid_minimal() -> bytes:
    """
    Buat PDF satu halaman kosong yang valid secara struktur (bisa dibuka
    pembaca PDF), tanpa perlu dependency tambahan seperti reportlab.
    """
    pdf = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
190
%%EOF"""
    return pdf


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# =============================================================================
# TEST 1 — Dekripsi dengan password salah harus DITOLAK
# =============================================================================
def test_decrypt_wrong_password_rejected():
    plaintext = "Data rahasia yang tidak boleh terbaca oleh siapapun."
    ciphertext_b64 = encrypt_text(plaintext, PASSWORD_BENAR)

    with pytest.raises(ValueError):
        decrypt_text(ciphertext_b64, PASSWORD_SALAH)


# =============================================================================
# TEST 2 — Ciphertext yang dimanipulasi (1 byte) harus DITOLAK
# (memverifikasi authentication tag AEAD benar-benar berfungsi)
# =============================================================================
def test_decrypt_tampered_ciphertext_rejected():
    import base64

    plaintext = "Pesan ini akan dirusak satu byte pada bagian ciphertext-nya."
    ciphertext_b64 = encrypt_text(plaintext, PASSWORD_BENAR)

    combined = bytearray(base64.b64decode(ciphertext_b64))

    # Struktur: salt(16) + nonce(12) + ciphertext+tag(sisanya)
    # Ubah 1 byte SETELAH offset 28, yaitu di bagian ciphertext/tag,
    # supaya perubahan pasti mengenai data yang diautentikasi.
    idx_target = 28  # byte pertama ciphertext (setelah salt+nonce)
    combined[idx_target] ^= 0xFF  # balik semua bit di byte tsb

    ciphertext_rusak_b64 = base64.b64encode(bytes(combined)).decode()

    with pytest.raises(ValueError):
        decrypt_text(ciphertext_rusak_b64, PASSWORD_BENAR)


# =============================================================================
# TEST 3 — Round-trip file gambar & PDF harus identik bit-per-bit (SHA-256)
# =============================================================================
def test_decrypt_image_and_pdf_roundtrip(tmp_path):
    kasus_uji = [
        ("contoh_gambar.png", _buat_png_valid_minimal()),
        ("contoh_dokumen.pdf", _buat_pdf_valid_minimal()),
    ]

    for algoritma in ("aes", "chacha"):
        for nama_file, data_asli in kasus_uji:
            path_asli = tmp_path / nama_file
            path_enc = tmp_path / f"{nama_file}.enc"
            path_dec = tmp_path / f"dec_{nama_file}"

            path_asli.write_bytes(data_asli)

            encrypt_file(str(path_asli), str(path_enc), PASSWORD_BENAR, algorithm=algoritma)
            decrypt_file(str(path_enc), str(path_dec), PASSWORD_BENAR, algorithm=algoritma)

            data_hasil = path_dec.read_bytes()

            hash_asli = _sha256(data_asli)
            hash_hasil = _sha256(data_hasil)

            assert hash_asli == hash_hasil, (
                f"Hash SHA-256 tidak cocok untuk {nama_file} ({algoritma}): "
                f"{hash_asli} != {hash_hasil}"
            )
