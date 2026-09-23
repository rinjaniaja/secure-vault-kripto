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
    """Login harus mengembalikan token JWT."""
    response = client.post("/login", json={"username": "agnia"})
    assert response.status_code == 200
    assert "token" in response.json


def test_encrypt_decrypt_roundtrip_with_valid_token(client):
    """Dengan token valid, enkripsi lalu dekripsi harus balik ke plaintext asli."""
    login_response = client.post("/login", json={"username": "agnia"})
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