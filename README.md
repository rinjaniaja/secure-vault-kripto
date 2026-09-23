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
