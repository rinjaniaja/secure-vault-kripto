"""
Script pengujian wajib untuk Topik A: Aplikasi Enkripsi Modern
Menjalankan semua pengujian sesuai soal dan menyimpan hasil ke Excel.
"""
import os
import sys
import time
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from crypto_utils import (
    derive_key,
    encrypt_text, decrypt_text,
    encrypt_text_chacha, decrypt_text_chacha,
    encrypt_file, decrypt_file,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Folder berkas uji (bagian luaran: "berkas uji" pada Bagian 5 dokumen tugas).
# Letakkan gambar dan PDF ASLI dengan nama gambar_uji.png dan dokumen_uji.pdf
# di folder ini sebelum menjalankan script. Kalau belum ada, script membuat
# berkas valid otomatis dan menyimpannya di sini.
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files")
os.makedirs(TEST_FILES_DIR, exist_ok=True)


# =========================================================
# HELPER: berkas GAMBAR dan PDF untuk uji kebenaran dekripsi
# =========================================================
def _buat_png_valid() -> bytes:
    """PNG kecil (32x32) yang valid, dibuat memakai Pillow."""
    from PIL import Image
    import io as _io

    img = Image.new("RGB", (32, 32), color=(80, 120, 200))
    buf = _io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _buat_pdf_valid() -> bytes:
    """PDF satu halaman kosong yang valid secara struktur (tanpa dependency
    tambahan), bisa dibuka pembaca PDF standar."""
    return b"""%PDF-1.4
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
186
%%EOF"""


def _ambil_berkas_uji(nama: str, pembuat) -> bytes:
    """Pakai berkas asli di benchmark/test_files/ bila ada. Kalau belum ada,
    buat otomatis lalu simpan di sana supaya ikut menjadi berkas uji."""
    path = os.path.join(TEST_FILES_DIR, nama)
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(pembuat())
    with open(path, "rb") as f:
        return f.read()


# =========================================================
# 1. KEBENARAN DEKRIPSI - 10 INPUT BERBEDA
# =========================================================
def uji_kebenaran_dekripsi():
    print("\n[1] Menguji kebenaran dekripsi pada 10 input berbeda...")
    password = "TestPassword123!"
    hasil = []

    # 8 input teks bervariasi + 2 berkas (gambar & PDF)
    input_teks = [
        "Halo dunia",
        "A" * 500,
        "Karakter spesial: !@#$%^&*()_+-=",
        "Emoji test 🔒🔑✅",
        "",  # string kosong
        "Baris1\nBaris2\nBaris3",
        "1234567890" * 10,
        "Teks unicode: 你好世界 مرحبا",
    ]

    for i, teks in enumerate(input_teks, 1):
        enc = encrypt_text(teks, password)
        dec = decrypt_text(enc, password)
        benar = (dec == teks)
        hasil.append({"No": i, "Jenis Input": f"Teks #{i}", "Ukuran (byte)": len(teks.encode()), "Berhasil": benar})

    # Berkas gambar dan PDF (syarat eksplisit dosen: minimal 1 gambar dan 1 PDF)
    file_tests = [
        ("gambar_uji.png", _ambil_berkas_uji("gambar_uji.png", _buat_png_valid)),
        ("dokumen_uji.pdf", _ambil_berkas_uji("dokumen_uji.pdf", _buat_pdf_valid)),
    ]
    for i, (nama, data) in enumerate(file_tests, 9):
        in_path = os.path.join(OUTPUT_DIR, nama)
        enc_path = in_path + ".enc"
        dec_path = os.path.join(OUTPUT_DIR, "dec_" + nama)
        with open(in_path, "wb") as f:
            f.write(data)
        encrypt_file(in_path, enc_path, password)
        decrypt_file(enc_path, dec_path, password)
        with open(dec_path, "rb") as f:
            benar = f.read() == data
        hasil.append({"No": i, "Jenis Input": nama, "Ukuran (byte)": len(data), "Berhasil": benar})
        for p in (in_path, enc_path, dec_path):
            os.remove(p)

    df = pd.DataFrame(hasil)
    print(df.to_string(index=False))
    return df


# =========================================================
# 2. WAKTU ENKRIPSI/DEKRIPSI - 1KB, 1MB, 10MB
# =========================================================
def uji_waktu_proses():
    print("\n[2] Mengukur waktu enkripsi/dekripsi untuk berbagai ukuran file...")
    password = "TestPassword123!"
    ukuran_list = [("1 KB", 1024), ("1 MB", 1024 * 1024), ("10 MB", 10 * 1024 * 1024)]
    hasil = []

    for label, ukuran in ukuran_list:
        data = os.urandom(ukuran)
        in_path = os.path.join(OUTPUT_DIR, "temp_input.bin")
        enc_path = os.path.join(OUTPUT_DIR, "temp_enc.bin")
        dec_path = os.path.join(OUTPUT_DIR, "temp_dec.bin")
        with open(in_path, "wb") as f:
            f.write(data)

        for algo in ["aes", "chacha"]:
            t0 = time.perf_counter()
            encrypt_file(in_path, enc_path, password, algorithm=algo)
            t_enc = time.perf_counter() - t0

            t0 = time.perf_counter()
            decrypt_file(enc_path, dec_path, password, algorithm=algo)
            t_dec = time.perf_counter() - t0

            hasil.append({
                "Ukuran": label,
                "Algoritma": "AES-256-GCM" if algo == "aes" else "ChaCha20-Poly1305",
                "Waktu Enkripsi (ms)": round(t_enc * 1000, 3),
                "Waktu Dekripsi (ms)": round(t_dec * 1000, 3),
            })

        for p in (in_path, enc_path, dec_path):
            if os.path.exists(p):
                os.remove(p)

    df = pd.DataFrame(hasil)
    print(df.to_string(index=False))
    return df


# =========================================================
# 3. AVALANCHE EFFECT
# =========================================================
def _bit_beda(bytes1: bytes, bytes2: bytes):
    """Return (jumlah bit berbeda, total bit yang dibandingkan)."""
    panjang = min(len(bytes1), len(bytes2))
    beda = 0
    for i in range(panjang):
        beda += bin(bytes1[i] ^ bytes2[i]).count("1")
    return beda, panjang * 8


def uji_avalanche_effect():
    """
    Avalanche effect: persentase bit cipherteks yang berubah bila SATU bit
    plainteks atau SATU karakter password (kunci) diubah.

    PENTING (metodologi): salt dan nonce DIKUNCI tetap khusus di pengujian ini.
    Aplikasi asli membuat salt dan nonce acak di setiap enkripsi, sehingga dua
    cipherteks selalu berbeda ~50% walau inputnya identik. Kalau tidak dikunci,
    angka yang keluar bukan efek dari perubahan 1 bit. Salt dan nonce tetap ini
    HANYA dipakai di pengujian, tidak pernah di aplikasi.

    Hasil untuk plainteks dipisah: badan cipherteks dan tag autentikasi (16 byte
    terakhir). GCM dan ChaCha20-Poly1305 bekerja seperti stream cipher (badan
    cipherteks = plainteks XOR keystream), sehingga 1 bit plainteks hanya mengubah
    1 bit badan cipherteks, sedangkan tag berubah total.
    """
    print("\n[3] Menghitung avalanche effect (salt & nonce dikunci)...")
    password = "TestPassword123!"
    password_ubah = password[:-1] + "X"
    salt = bytes(16)    # dikunci tetap, khusus pengujian
    nonce = bytes(12)   # dikunci tetap, khusus pengujian

    plaintext = ("Pesan uji avalanche effect untuk enkripsi modern AES dan ChaCha20" * 3).encode()
    plaintext_ubah = bytearray(plaintext)
    plaintext_ubah[-1] ^= 0x01          # ubah tepat 1 bit
    plaintext_ubah = bytes(plaintext_ubah)

    hasil = []
    for nama, cls in [("AES-256-GCM", AESGCM), ("ChaCha20-Poly1305", ChaCha20Poly1305)]:
        kunci = derive_key(password, salt)[0]
        kunci_ubah = derive_key(password_ubah, salt)[0]

        dasar = cls(kunci).encrypt(nonce, plaintext, None)
        ct_plain = cls(kunci).encrypt(nonce, plaintext_ubah, None)
        ct_pass = cls(kunci_ubah).encrypt(nonce, plaintext, None)

        b_body, n_body = _bit_beda(dasar[:-16], ct_plain[:-16])
        b_tag, n_tag = _bit_beda(dasar[-16:], ct_plain[-16:])
        b_all, n_all = _bit_beda(dasar, ct_plain)
        b_pw, n_pw = _bit_beda(dasar, ct_pass)

        hasil.append({
            "Algoritma": nama,
            "1 bit plaintext: badan cipherteks (%)": round(b_body / n_body * 100, 3),
            "1 bit plaintext: tag autentikasi (%)": round(b_tag / n_tag * 100, 2),
            "1 bit plaintext: keseluruhan (%)": round(b_all / n_all * 100, 2),
            "1 karakter password: keseluruhan (%)": round(b_pw / n_pw * 100, 2),
        })

    df = pd.DataFrame(hasil)
    print(df.to_string(index=False))
    print("Catatan: ubah password mengubah kunci sehingga seluruh keystream berubah (~50%).")
    print("Ubah 1 bit plaintext hanya mengubah 1 bit badan cipherteks (sifat mode stream);")
    print("integritas dijaga oleh tag autentikasi yang berubah ~50%.")
    return df


# =========================================================
# 4. ENTROPI & HISTOGRAM
# =========================================================
def hitung_entropi(data: bytes) -> float:
    """Menghitung entropi Shannon (bit per byte) dari data."""
    if len(data) == 0:
        return 0.0
    _, counts = np.unique(np.frombuffer(data, dtype=np.uint8), return_counts=True)
    probabilitas = counts / len(data)
    entropi = -np.sum(probabilitas * np.log2(probabilitas))
    return entropi


def uji_entropi_histogram():
    print("\n[4] Menghitung entropi dan membuat histogram byte...")
    password = "TestPassword123!"
    plaintext = ("Ini adalah contoh teks plaintext yang cukup panjang untuk dianalisis "
                 "distribusi byte-nya secara statistik. " * 20)

    enc_aes = base64.b64decode(encrypt_text(plaintext, password))
    enc_chacha = base64.b64decode(encrypt_text_chacha(plaintext, password))

    entropi_plain = hitung_entropi(plaintext.encode())
    entropi_aes = hitung_entropi(enc_aes)
    entropi_chacha = hitung_entropi(enc_chacha)

    hasil = pd.DataFrame([
        {"Data": "Plaintext asli", "Entropi (bit/byte)": round(entropi_plain, 4)},
        {"Data": "Cipherteks AES-256-GCM", "Entropi (bit/byte)": round(entropi_aes, 4)},
        {"Data": "Cipherteks ChaCha20-Poly1305", "Entropi (bit/byte)": round(entropi_chacha, 4)},
    ])
    print(hasil.to_string(index=False))
    print("Catatan: entropi maksimum teoretis adalah 8 bit/byte (distribusi byte seragam/acak sempurna).")

    # Bikin histogram
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, data, judul in zip(
        axes,
        [plaintext.encode(), enc_aes, enc_chacha],
        ["Plaintext", "Cipherteks AES-GCM", "Cipherteks ChaCha20"]
    ):
        ax.hist(list(data), bins=256, range=(0, 255), color="steelblue")
        ax.set_title(judul)
        ax.set_xlabel("Nilai byte (0-255)")
        ax.set_ylabel("Frekuensi")
    plt.tight_layout()
    histogram_path = os.path.join(OUTPUT_DIR, "histogram_byte.png")
    plt.savefig(histogram_path, dpi=120)
    plt.close()
    print(f"Histogram disimpan di: {histogram_path}")

    return hasil


# =========================================================
# JALANKAN SEMUA & SIMPAN KE EXCEL
# =========================================================
def main():
    print("=" * 60)
    print("PENGUJIAN WAJIB - APLIKASI ENKRIPSI MODERN (TOPIK A)")
    print("=" * 60)

    df_kebenaran = uji_kebenaran_dekripsi()
    df_waktu = uji_waktu_proses()
    df_avalanche = uji_avalanche_effect()
    df_entropi = uji_entropi_histogram()

    excel_path = os.path.join(OUTPUT_DIR, "hasil_pengujian.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_kebenaran.to_excel(writer, sheet_name="1_Kebenaran_Dekripsi", index=False)
        df_waktu.to_excel(writer, sheet_name="2_Waktu_Proses", index=False)
        df_avalanche.to_excel(writer, sheet_name="3_Avalanche_Effect", index=False)
        df_entropi.to_excel(writer, sheet_name="4_Entropi", index=False)

    print("\n" + "=" * 60)
    print(f"SELESAI! Semua hasil disimpan di: {excel_path}")
    print(f"Histogram disimpan di: {os.path.join(OUTPUT_DIR, 'histogram_byte.png')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
