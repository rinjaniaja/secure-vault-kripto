"""
image_encryption_demo.py
=============================================================================
FITUR PENGAYAAN — ENKRIPSI CITRA: VISUALISASI ECB VS MODE AMAN (AES-GCM)
Tugas UTS Keamanan Informasi — Topik A: Aplikasi Enkripsi Modern
Dikerjakan oleh: Serli Nadia Azzahra

TUJUAN
------
Menunjukkan secara visual mengapa mode ECB (Electronic Codebook) TIDAK AMAN
untuk data seperti citra, dibandingkan dengan mode AEAD yang sudah dipakai
di aplikasi utama (AES-256-GCM, lihat crypto_utils.py).

Kenapa ECB bocor pola?
-----------------------
ECB mengenkripsi setiap blok plaintext 16-byte secara independen dengan kunci
yang sama:  C_i = E(K, P_i)
Konsekuensinya: BLOK PLAINTEXT YANG SAMA -> SELALU MENGHASILKAN BLOK
CIPHERTEXT YANG SAMA. Kalau citra punya area warna solid (blok piksel yang
identik/berulang), pola itu akan tetap terlihat di ciphertext -- cuma
warnanya beda, bentuknya tetap kelihatan. Ini sesuai instruksi dosen bahwa
mode ECB HANYA boleh muncul sebagai PEMBANDING (bukan mode yang dipakai
untuk keamanan sungguhan di aplikasi).

Kenapa AES-GCM aman?
---------------------
AES-GCM adalah mode CTR (Counter) yang dikombinasikan dengan autentikasi
GHASH. Di mode CTR, setiap blok plaintext di-XOR dengan keystream unik yang
dihasilkan dari kombinasi (kunci, nonce, nomor counter blok). Karena
keystream berbeda untuk setiap blok meskipun plaintext-nya identik, blok
plaintext yang sama TIDAK menghasilkan blok ciphertext yang sama. Hasilnya
terlihat seperti derau/noise acak sempurna, tanpa pola apa pun -- inilah
yang dipakai crypto_utils.py (encrypt_file, encrypt_text) di aplikasi utama.

CATATAN PENTING SOAL DEMO INI
------------------------------
- Fungsi ECB di file ini DIBUAT KHUSUS untuk demonstrasi kelemahan, TIDAK
  dipakai atau diekspos di app.py / crypto_utils.py mode aman aplikasi.
- Kunci diturunkan dengan derive_key() dari crypto_utils.py yang sudah ada,
  supaya konsisten dengan skema KDF (scrypt + salt acak) yang dipakai di
  seluruh proyek.
- Untuk AES-GCM, yang divisualisasikan sebagai "citra acak" adalah byte
  ciphertext murni (tanpa auth tag & nonce), diletakkan ulang ke dimensi
  citra asli -- supaya perbandingan piksel-ke-piksel adil dengan hasil ECB.

Output:
  output/1_original.png       -> citra asli (pola blok warna solid)
  output/2_encrypted_ecb.png  -> hasil ECB (pola MASIH TERLIHAT)
  output/3_encrypted_gcm.png  -> hasil AES-GCM (acak, tanpa pola)
  output/4_perbandingan.png   -> ketiganya digabung berdampingan (untuk laporan)
"""

import os
from PIL import Image, ImageDraw

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Pakai fungsi yang SUDAH ADA di crypto_utils.py supaya konsisten
# dengan skema KDF (scrypt + salt acak) di seluruh proyek.
from crypto_utils import derive_key

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BLOCK_SIZE = 16  # ukuran blok AES dalam byte


# =============================================================================
# 1. BUAT CITRA DEMO (pola blok warna solid supaya kelemahan ECB kelihatan)
# =============================================================================
def buat_citra_demo(lebar: int = 256, tinggi: int = 256) -> Image.Image:
    """
    Membuat citra bitmap sederhana berisi blok-blok warna solid berulang
    (mirip logo sederhana). Pola berulang ini PENTING supaya kelemahan ECB
    (blok plaintext sama -> blok ciphertext sama) bisa terlihat jelas.
    """
    img = Image.new("RGB", (lebar, tinggi), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    ukuran_kotak = 32
    warna_a = (30, 60, 200)   # biru
    warna_b = (230, 230, 235)  # abu terang

    # Pola papan catur (checkerboard) dari kotak-kotak solid berulang
    for y in range(0, tinggi, ukuran_kotak):
        for x in range(0, lebar, ukuran_kotak):
            kotak_ganjil = ((x // ukuran_kotak) + (y // ukuran_kotak)) % 2 == 0
            warna = warna_a if kotak_ganjil else warna_b
            draw.rectangle([x, y, x + ukuran_kotak, y + ukuran_kotak], fill=warna)

    # Tambahkan lingkaran solid di tengah agar makin jelas ada pola berulang
    draw.ellipse(
        [lebar // 2 - 48, tinggi // 2 - 48, lebar // 2 + 48, tinggi // 2 + 48],
        fill=(200, 30, 30),
    )
    return img


# =============================================================================
# 2. ENKRIPSI MODE ECB (HANYA UNTUK DEMONSTRASI KELEMAHAN)
# =============================================================================
def enkripsi_ecb(data: bytes, password: str) -> tuple[bytes, bytes]:
    """
    Enkripsi byte mentah dengan AES-ECB.

    PERINGATAN: Mode ECB TIDAK AMAN untuk data nyata dan HANYA dipakai di
    sini sebagai pembanding edukatif, sesuai instruksi dosen. Mode ini TIDAK
    dipakai di crypto_utils.py maupun app.py (aplikasi utama tetap 100%
    memakai AEAD: AES-256-GCM / ChaCha20-Poly1305).

    Return: (ciphertext, salt) -- salt perlu disimpan untuk penurunan
    ulang kunci saat dekripsi (tidak dipakai lebih lanjut di demo ini
    karena tujuannya hanya visualisasi).
    """
    key, salt = derive_key(password)  # reuse derive_key dari crypto_utils.py

    # ECB tidak pakai IV/nonce -- inilah salah satu kelemahannya
    padder = padding.PKCS7(BLOCK_SIZE * 8).padder()
    data_padded = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data_padded) + encryptor.finalize()

    return ciphertext, salt


# =============================================================================
# 3. ENKRIPSI MODE AMAN: AES-256-GCM
# =============================================================================
def enkripsi_gcm(data: bytes, password: str) -> tuple[bytes, bytes, bytes, bytes]:
    """
    Enkripsi byte mentah dengan AES-256-GCM (mode aman, AEAD).
    Setiap blok di-XOR dengan keystream unik (mode counter), sehingga blok
    plaintext yang identik TIDAK menghasilkan blok ciphertext yang sama.

    Return: (ciphertext_dengan_tag, ciphertext_murni_tanpa_tag, nonce, salt)
    ciphertext_murni_tanpa_tag dipakai untuk divisualisasikan sebagai citra
    "noise" dengan ukuran byte yang sama persis dengan plaintext asli
    (GCM adalah stream cipher, tidak butuh padding).
    """
    key, salt = derive_key(password)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext_dengan_tag = aesgcm.encrypt(nonce, data, None)

    # 16 byte terakhir adalah authentication tag, sisanya ciphertext murni
    ciphertext_murni = ciphertext_dengan_tag[:-16]

    return ciphertext_dengan_tag, ciphertext_murni, nonce, salt


# =============================================================================
# 4. UBAH BYTE HASIL ENKRIPSI KEMBALI JADI CITRA UNTUK DIBANDINGKAN
# =============================================================================
def bytes_ke_citra(data: bytes, ukuran: tuple[int, int], mode: str = "RGB") -> Image.Image:
    """Potong/pad byte agar pas ke dimensi citra asli, lalu bentuk jadi Image."""
    lebar, tinggi = ukuran
    channel = len(mode)  # "RGB" -> 3
    total_byte_dibutuhkan = lebar * tinggi * channel

    if len(data) < total_byte_dibutuhkan:
        data = data + bytes(total_byte_dibutuhkan - len(data))  # pad nol
    else:
        data = data[:total_byte_dibutuhkan]

    return Image.frombytes(mode, ukuran, data)


# =============================================================================
# 5. GABUNGKAN 3 CITRA JADI SATU FILE PERBANDINGAN (untuk laporan)
# =============================================================================
def buat_gambar_perbandingan(citra_list: list[Image.Image], judul_list: list[str]) -> Image.Image:
    from PIL import ImageFont

    lebar_satu = citra_list[0].width
    tinggi_satu = citra_list[0].height
    padding_label = 30
    spasi = 10

    lebar_total = lebar_satu * len(citra_list) + spasi * (len(citra_list) - 1)
    tinggi_total = tinggi_satu + padding_label

    gabungan = Image.new("RGB", (lebar_total, tinggi_total), color=(255, 255, 255))
    draw = ImageDraw.Draw(gabungan)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    x_offset = 0
    for citra, judul in zip(citra_list, judul_list):
        gabungan.paste(citra, (x_offset, padding_label))
        draw.text((x_offset + 5, 8), judul, fill=(0, 0, 0), font=font)
        x_offset += citra.width + spasi

    return gabungan


# =============================================================================
# MAIN
# =============================================================================
def main():
    password = "PasswordDemoECBvsGCM123!"  # nilai contoh HANYA untuk demo lokal ini

    print("=" * 70)
    print("DEMO: VISUALISASI KELEMAHAN MODE ECB vs MODE AMAN (AES-256-GCM)")
    print("=" * 70)

    # 1. Buat & simpan citra asli
    citra_asli = buat_citra_demo()
    path_asli = os.path.join(OUTPUT_DIR, "1_original.png")
    citra_asli.save(path_asli)
    print(f"[1] Citra asli disimpan: {path_asli}")

    data_piksel = citra_asli.tobytes()  # byte mentah RGB, ini yang dienkripsi

    # 2. Enkripsi ECB
    ciphertext_ecb, _ = enkripsi_ecb(data_piksel, password)
    citra_ecb = bytes_ke_citra(ciphertext_ecb, citra_asli.size, mode="RGB")
    path_ecb = os.path.join(OUTPUT_DIR, "2_encrypted_ecb.png")
    citra_ecb.save(path_ecb)
    print(f"[2] Hasil enkripsi ECB disimpan: {path_ecb}")
    print("    -> Perhatikan: pola kotak & lingkaran ASLI MASIH TERLIHAT!")

    # 3. Enkripsi AES-GCM
    _, ciphertext_gcm_murni, _, _ = enkripsi_gcm(data_piksel, password)
    citra_gcm = bytes_ke_citra(ciphertext_gcm_murni, citra_asli.size, mode="RGB")
    path_gcm = os.path.join(OUTPUT_DIR, "3_encrypted_gcm.png")
    citra_gcm.save(path_gcm)
    print(f"[3] Hasil enkripsi AES-GCM disimpan: {path_gcm}")
    print("    -> Perhatikan: hasilnya benar-benar noise acak, TANPA pola.")

    # 4. Gabungkan jadi satu gambar perbandingan untuk laporan
    gabungan = buat_gambar_perbandingan(
        [citra_asli, citra_ecb, citra_gcm],
        ["Asli", "ECB (BOCOR POLA)", "AES-GCM (AMAN)"],
    )
    path_gabungan = os.path.join(OUTPUT_DIR, "4_perbandingan.png")
    gabungan.save(path_gabungan)
    print(f"[4] Gambar perbandingan (untuk laporan) disimpan: {path_gabungan}")

    print("\nKESIMPULAN:")
    print("- ECB mengenkripsi tiap blok 16-byte secara independen dengan kunci")
    print("  yang sama -> blok plaintext identik selalu menghasilkan blok")
    print("  ciphertext identik -> pola citra asli BOCOR ke ciphertext.")
    print("- AES-GCM (mode CTR + autentikasi GHASH) meng-XOR tiap blok dengan")
    print("  keystream unik -> tidak ada korelasi berulang -> hasil terlihat")
    print("  seperti derau acak sempurna, sesuai prinsip 'ciphertext")
    print("  indistinguishability' yang diharapkan dari enkripsi modern.")
    print("=" * 70)


if __name__ == "__main__":
    main()
