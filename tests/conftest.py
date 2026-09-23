"""
conftest.py — dijalankan otomatis oleh pytest sebelum test lain.
Menyediakan environment variable dummy khusus untuk pengujian,
supaya api.py bisa di-import tanpa perlu set manual tiap kali testing.
"""
import os

os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test_only_secret_key_jangan_dipakai_di_production_1234567890abcdef",
)
os.environ.setdefault(
    "APP_USERS",
    "agnia:testpassword123,bunga:testpassword456",
)