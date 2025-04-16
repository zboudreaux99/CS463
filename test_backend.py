import os
from fastapi.testclient import TestClient
from backend import app

client = TestClient(app)

def test_generate_rsa_keys():
    response = client.get("/generate_keys")
    assert response.status_code == 200
    data = response.json()
    assert "public_key" in data
    assert "private_key" in data

def test_sign_and_verify():
    # First, generate a key pair
    keys_response = client.get("/generate_keys")
    keys = keys_response.json()
    private_key = keys["private_key"]
    public_key = keys["public_key"]
    
    # Save the private key temporarily to send as file in sign endpoint
    with open("temp_private.pem", "w") as f:
        f.write(private_key)
    
    message = "Test message"
    
    with open("temp_private.pem", "rb") as file:
        sign_response = client.post(
            "/sign",
            data={"message": message},
            files={"private_key": ("temp_private.pem", file, "application/x-pem-file")}
        )
    
    os.remove("temp_private.pem")
    assert sign_response.status_code == 200
    signature = sign_response.json().get("signature")
    assert signature is not None

    # Prepare verify payload
    verify_payload = {
        "public_key": public_key,
        "message": message,
        "signature": signature
    }
    verify_response = client.post("/verify", json=verify_payload)
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data.get("valid") is True

def test_aes_encrypt_decrypt():
    password = "strongpassword"
    plaintext = "This is a secret message."
    
    # Encrypt
    encrypt_payload = {
        "password": password,
        "plaintext": plaintext
    }
    encrypt_response = client.post("/aes_encrypt", json=encrypt_payload)
    assert encrypt_response.status_code == 200
    encrypt_data = encrypt_response.json()
    for key in ["ciphertext", "salt", "iv"]:
        assert key in encrypt_data
    
    # Decrypt
    decrypt_payload = {
        "password": password,
        "ciphertext": encrypt_data["ciphertext"],
        "salt": encrypt_data["salt"],
        "iv": encrypt_data["iv"]
    }
    decrypt_response = client.post("/aes_decrypt", json=decrypt_payload)
    assert decrypt_response.status_code == 200
    decrypt_data = decrypt_response.json()
    assert decrypt_data.get("plaintext") == plaintext
