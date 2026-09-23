# Secure Vault — Aplikasi Enkripsi Modern

## Deskripsi
Secure Vault adalah aplikasi enkripsi dan dekripsi teks maupun berkas menggunakan algoritma AES-256-GCM (dengan pembanding ChaCha20-Poly1305). Kunci enkripsi diturunkan dari kata sandi pengguna menggunakan scrypt dengan salt acak, dan setiap proses enkripsi menghasilkan IV/nonce acak yang disimpan bersama cipherteks. Aplikasi menolak proses dekripsi apabila kata sandi salah atau cipherteks telah diubah.

## Anggota Kelompok
- Bunga Denis Rinjani - 247006111064
- Agnia Nazwan R - 247006111076
- Serli Nadia Azzahra - 247006111080

## Cara Instalasi

1. Pastikan Python 3.9 atau lebih baru sudah terinstall. Cek dengan `python --version`

2. Clone repository ini:
`git clone https://github.com/rinjaniaja/secure-vault-kripto.git`
lalu masuk ke foldernya dengan `cd secure-vault-kripto`

3. Buat virtual environment dengan `python -m venv venv`

4. Aktifkan virtual environment. Untuk Windows gunakan `venv\Scripts\activate`, untuk Mac/Linux gunakan `source venv/bin/activate`

5. Install seluruh dependency dengan `pip install -r requirements.txt`

## Cara Menjalankan

Untuk menjalankan aplikasi web, gunakan perintah `streamlit run app.py`. Aplikasi akan otomatis terbuka di browser pada alamat http://localhost:8501

Untuk menjalankan unit test, gunakan perintah `pytest tests/ -v`

Untuk menjalankan script pengujian wajib yang menghasilkan file Excel dan histogram, gunakan perintah `python benchmark/run_tests.py`. Hasilnya akan tersimpan di folder benchmark/output/ berupa hasil_pengujian.xlsx dan histogram_byte.png

## Contoh Penggunaan

### Enkripsi Teks
Buka aplikasi web, pilih menu Enkripsi/Dekripsi Teks, lalu pilih tab Enkripsi. Masukkan teks dan password, pilih algoritma (AES-256-GCM atau ChaCha20-Poly1305), lalu klik tombol enkripsi. Hasil ciphertext dalam format Base64 akan muncul dan bisa disalin.

### Dekripsi Teks
Pilih tab Dekripsi, tempel ciphertext Base64 yang ingin didekripsi, masukkan password yang sama saat enkripsi, pilih algoritma yang sesuai, lalu klik tombol dekripsi. Jika password benar dan data tidak berubah, teks asli akan muncul kembali. Jika password salah atau data telah diubah, aplikasi akan menampilkan pesan penolakan.

### Enkripsi/Dekripsi File
Pilih menu Enkripsi/Dekripsi File. Untuk enkripsi, upload file seperti gambar atau PDF, masukkan password, klik enkripsi, lalu unduh file hasil berekstensi .enc. Untuk dekripsi, upload file .enc tersebut, masukkan password yang sama, klik dekripsi, lalu unduh file hasil yang sudah kembali ke bentuk aslinya.

## Fitur Pengayaan

### 1. Hybrid Encryption (RSA-OAEP + AES-256-GCM)
Modul `hybrid_crypto.py` menyediakan enkripsi hybrid: session key AES-256 dibangkitkan acak, dipakai untuk mengenkripsi data dengan AES-256-GCM, lalu session key tersebut dibungkus dengan RSA-OAEP (padding MGF1-SHA256) memakai public key penerima. Modul ini dipakai lewat kode Python langsung (belum terhubung ke antarmuka Streamlit), fungsi utamanya: `generate_rsa_keypair()`, `encrypt_hybrid()`, dan `decrypt_hybrid()`.

### 2. REST API dengan Autentikasi JWT (HMAC-SHA512)
Modul `api.py` menyediakan REST API berbasis Flask dengan endpoint `/login`, `/encrypt`, dan `/decrypt`. Endpoint `/encrypt` dan `/decrypt` wajib menyertakan token JWT (didapat dari `/login`) di header `Authorization: Bearer <token>`.

Sebelum menjalankan `api.py`, dua environment variable berikut **wajib** diset lebih dulu (aplikasi akan menolak berjalan jika belum diset, demi keamanan — tidak ada kunci atau kredensial yang ditulis di kode sumber):

- `JWT_SECRET_KEY` — kunci rahasia untuk menandatangani token JWT, disarankan minimal 64 byte acak
- `APP_USERS` — daftar pengguna yang diizinkan login, format `username1:password1,username2:password2`

**Windows (Command Prompt):**
```
set JWT_SECRET_KEY=isi_dengan_kunci_acak_minimal_64_karakter
set APP_USERS=bunga:passwordBunga,agnia:passwordAgnia,serli:passwordSerli
python api.py
```

**Mac/Linux:**
```
export JWT_SECRET_KEY=isi_dengan_kunci_acak_minimal_64_karakter
export APP_USERS=bunga:passwordBunga,agnia:passwordAgnia,serli:passwordSerli
python api.py
```

Server akan berjalan di `http://127.0.0.1:5000`.

**Contoh penggunaan lewat curl:**

1. Login untuk mendapatkan token:
```
curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d "{\"username\":\"bunga\",\"password\":\"passwordBunga\"}"
```

2. Enkripsi teks (ganti `TOKEN` dengan token dari langkah 1):
```
curl -X POST http://127.0.0.1:5000/encrypt -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -d "{\"plaintext\":\"pesan rahasia\",\"password\":\"pass123\"}"
```

3. Dekripsi teks (ganti `CIPHERTEXT` dengan hasil dari langkah 2):
```
curl -X POST http://127.0.0.1:5000/decrypt -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -d "{\"ciphertext\":\"CIPHERTEXT\",\"password\":\"pass123\"}"
```

Catatan: `hybrid_crypto.py` dan `api.py` berjalan sebagai modul/server terpisah dari antarmuka Streamlit (`app.py`), sesuai desain arsitektur yang memisahkan fitur inti (UI interaktif) dari fitur pengayaan (modul mandiri dan layanan API).
