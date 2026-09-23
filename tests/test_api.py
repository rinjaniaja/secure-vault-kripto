"""Unit test untuk api.py"""

import pytest
from api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_encrypt_without_token_rejected(client):
    """Akses /encrypt tanpa token harus ditolak (401)."""
    response = client.post("/encrypt", json={"plaintext": "test", "password": "1234"})
    assert response.status_code == 401


def test_encrypt_with_invalid_token_rejected(client):
    """Akses /encrypt dengan token invalid harus ditolak (403)."""
    headers = {"Authorization": "Bearer token_palsu_asal"}
    response = client.post("/encrypt", json={"plaintext": "test", "password": "1234"}, headers=headers)
    assert response.status_code == 403


def test_login_returns_token(client):
    """Login dengan username & password benar harus mengembalikan token JWT."""
    response = client.post("/login", json={"username": "agnia", "password": "testpassword123"})
    assert response.status_code == 200
    assert "token" in response.json


def test_login_wrong_password_rejected(client):
    """Login dengan password salah harus ditolak (401), TIDAK boleh keluar token."""
    response = client.post("/login", json={"username": "agnia", "password": "password_salah"})
    assert response.status_code == 401
    assert "token" not in response.json


def test_login_unknown_username_rejected(client):
    """Login dengan username yang tidak terdaftar harus ditolak (401)."""
    response = client.post("/login", json={"username": "orang_asing", "password": "apasaja"})
    assert response.status_code == 401


def test_encrypt_decrypt_roundtrip_with_valid_token(client):
    """Dengan token valid, enkripsi lalu dekripsi harus balik ke plaintext asli."""
    login_response = client.post("/login", json={"username": "agnia", "password": "testpassword123"})
    token = login_response.json["token"]
    headers = {"Authorization": f"Bearer {token}"}

    encrypt_response = client.post(
        "/encrypt",
        json={"plaintext": "pesan rahasia", "password": "password123"},
        headers=headers,
    )
    assert encrypt_response.status_code == 200
    ciphertext = encrypt_response.json["ciphertext"]

    decrypt_response = client.post(
        "/decrypt",
        json={"ciphertext": ciphertext, "password": "password123"},
        headers=headers,
    )
    assert decrypt_response.status_code == 200
    assert decrypt_response.json["plaintext"] == "pesan rahasia"