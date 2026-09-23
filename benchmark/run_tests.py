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

from crypto_utils import (
    encrypt_text, decrypt_text,
    encrypt_text_chacha, decrypt_text_chacha,
    encrypt_file, decrypt_file,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# 1. KEBENARAN DEKRIPSI - 10 INPUT BERBEDA
# =========================================================
def uji_kebenaran_dekripsi():
    print("\n[1] Menguji kebenaran dekripsi pada 10 input berbeda...")
    password = "TestPassword123!"
    hasil = []

    # 8 input teks bervariasi + 2 input file biner (simulasi gambar & PDF)
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

    # Input file biner (simulasi gambar & PDF dengan byte acak header khas)
    file_tests = [
        ("simulasi_gambar.png", b"\x89PNG\r\n\x1a\n" + os.urandom(2000)),
        ("simulasi_dokumen.pdf", b"%PDF-1.4\n" + os.urandom(3000)),
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
def hitung_avalanche(bytes1: bytes, bytes2: bytes) -> float:
    """Menghitung persentase bit yang berbeda antara dua rangkaian byte."""
    panjang = min(len(bytes1), len(bytes2))
    total_bit = panjang * 8
    bit_berbeda = 0
    for i in range(panjang):
        xor_result = bytes1[i] ^ bytes2[i]
        bit_berbeda += bin(xor_result).count("1")
    return (bit_berbeda / total_bit) * 100 if total_bit > 0 else 0


def uji_avalanche_effect():
    print("\n[3] Menghitung avalanche effect...")
    password = "TestPassword123!"
    plaintext = "Pesan uji avalanche effect untuk enkripsi modern AES dan ChaCha20" * 3
    hasil = []

    for algo_name, enc_func in [("AES-256-GCM", encrypt_text), ("ChaCha20-Poly1305", encrypt_text_chacha)]:
        # Kasus A: ubah 1 bit plaintext
        plaintext_asli = plaintext
        plaintext_ubah = plaintext[:-1] + chr(ord(plaintext[-1]) ^ 1)

        enc1 = base64.b64decode(enc_func(plaintext_asli, password))
        enc2 = base64.b64decode(enc_func(plaintext_ubah, password))
        avalanche_plaintext = hitung_avalanche(enc1, enc2)

        # Kasus B: ubah 1 karakter password
        password_asli = password
        password_ubah = password[:-1] + "X"

        enc3 = base64.b64decode(enc_func(plaintext_asli, password_asli))
        enc4 = base64.b64decode(enc_func(plaintext_asli, password_ubah))
        avalanche_key = hitung_avalanche(enc3, enc4)

        hasil.append({
            "Algoritma": algo_name,
            "Avalanche (ubah 1 bit plaintext) %": round(avalanche_plaintext, 2),
            "Avalanche (ubah 1 karakter password) %": round(avalanche_key, 2),
        })

    df = pd.DataFrame(hasil)
    print(df.to_string(index=False))
    print("Catatan: idealnya nilai avalanche mendekati 50% (perubahan acak/tidak terprediksi).")
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