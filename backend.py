from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RSAKeys(BaseModel):
    public_key: str
    private_key: str

class SignRequest(BaseModel):
    private_key: str
    message: str

class VerifyRequest(BaseModel):
    public_key: str
    message: str
    signature: str

class AESEncryptRequest(BaseModel):
    password: str
    plaintext: str

class AESDecryptRequest(BaseModel):
    password: str
    ciphertext: str
    salt: str
    iv: str

# Generate RSA key pair
@app.get("/generate_keys")
def generate_rsa_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    return {
        "public_key": public_key.decode(), 
        "private_key": private_key.decode()
    }

# Sign a message with RSA private key from uploaded file
@app.post("/sign")
def sign_message(private_key: UploadFile = File(...), message: str = Form(...)):
    try:
        private_key_data = private_key.file.read()
        key = RSA.import_key(private_key_data)

        h = SHA256.new(message.encode())

        signature = pkcs1_15.new(key).sign(h)
        encoded_signature = base64.b64encode(signature).decode()

        return {"signature": encoded_signature}
    except Exception as e:
        print(f"Error signing: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Verify RSA signature using public key
@app.post("/verify")
def verify_signature(req: VerifyRequest):
    try:
        key = RSA.import_key(req.public_key)
        h = SHA256.new(req.message.encode())

        try:
            decoded_signature = base64.b64decode(req.signature)
        except Exception as e:
            print(f"Error decoding signature: {str(e)}")
            return {"valid": False, "error": "Invalid signature format"}

        try:
            pkcs1_15.new(key).verify(h, decoded_signature)
            print("Signature is valid!")
            return {"valid": True}
        except (ValueError, TypeError) as e:
            print(f"Verification failed: {str(e)}")
            return {"valid": False, "error": str(e)}
    except Exception as e:
        print(f"General verification error: {str(e)}")
        return {"valid": False, "error": str(e)}

# AES Encryption
@app.post("/aes_encrypt")
def aes_encrypt(req: AESEncryptRequest):
    try:
        # Generate a random salt
        salt = get_random_bytes(16)
        
        # Derive key from password
        key = PBKDF2(req.password, salt, dkLen=32)
        
        # Create cipher with random IV
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Pad and encrypt the data
        padded_data = pad(req.plaintext.encode(), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        # Return everything needed for decryption
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "salt": base64.b64encode(salt).decode(),
            "iv": base64.b64encode(iv).decode()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# AES Decryption
@app.post("/aes_decrypt")
def aes_decrypt(req: AESDecryptRequest):
    try:
        # Decode base64 values
        salt = base64.b64decode(req.salt)
        iv = base64.b64decode(req.iv)
        ciphertext = base64.b64decode(req.ciphertext)
        
        # Derive the key from password
        key = PBKDF2(req.password, salt, dkLen=32)
        
        # Create cipher and decrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(ciphertext)
        
        # Unpad and decode the plaintext
        plaintext = unpad(padded_plaintext, AES.block_size).decode()
        
        return {"plaintext": plaintext}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)