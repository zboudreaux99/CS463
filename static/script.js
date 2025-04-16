const API_BASE = "http://localhost:8000";

console.log("script.js is loaded!");

// RSA Key Management Functions
function downloadKey(keyContent, filename) {
    const blob = new Blob([keyContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

async function generateRSAKeys() {
    try {
        const response = await fetch(`${API_BASE}/generate_keys`);

        if (!response.ok) {
            throw new Error(`HTTP error! State: ${response.status}`);
        }

        const data = await response.json();
        document.getElementById("rsa-keys").innerText = JSON.stringify(data, null, 2);
        
        // Store keys in global variables for download
        window.generatedPublicKey = data.public_key;
        window.generatedPrivateKey = data.private_key;
        
        // Show download buttons
        document.getElementById("download-keys-div").style.display = "block";
    } catch (error) {
        console.error(`Error generating keys: ${error}`);
        document.getElementById("rsa-keys").innerText = `Error generating keys: ${error.message}`;
    }
}

function downloadPublicKey() {
    if (window.generatedPublicKey) {
        downloadKey(window.generatedPublicKey, "public_key.pem");
    } else {
        alert("No public key available. Generate keys first.");
    }
}

function downloadPrivateKey() {
    if (window.generatedPrivateKey) {
        downloadKey(window.generatedPrivateKey, "private_key.pem");
    } else {
        alert("No private key available. Generate keys first.");
    }
}

// RSA Signature Functions
async function signMessage() {
    const privateKeyFile = document.getElementById("private-key").files[0];
    const message = document.getElementById("message").value;

    if (!privateKeyFile) {
        alert("Please upload a private key file.");
        return;
    }

    const formData = new FormData();
    formData.append("private_key", privateKeyFile);
    formData.append("message", message);

    console.log(`🔹 Signing message: '${message}'`);

    try {
        const response = await fetch(`${API_BASE}/sign`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        document.getElementById("signature").innerText = JSON.stringify(data, null, 2);
        
        // Automatically populate the verification fields with the same data
        document.getElementById("verify-message").value = message;
        document.getElementById("verify-signature").value = data.signature;
    } catch (error) {
        console.error("Error signing message:", error);
        document.getElementById("signature").innerText = `Error signing message: ${error.message}`;
    }
}

async function verifySignature() {
    const message = document.getElementById("verify-message").value;
    const signature = document.getElementById("verify-signature").value;
    const publicKeyFile = document.getElementById("public-key-file").files[0];

    if (!publicKeyFile || !signature) {
        alert("Please upload a public key file and provide a signature.");
        return;
    }

    const reader = new FileReader();

    reader.onload = async function (event) {
        const publicKeyContent = event.target.result;

        console.log("🔹 Sending Data for Verification:");
        console.log(`🔹 Message: '${message}'`);
        console.log(`🔹 Signature: '${signature}'`);
        console.log(`🔹 Public Key Content (first 50 chars): '${publicKeyContent.substring(0, 50)}...'`);

        try {
            const response = await fetch(`${API_BASE}/verify`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    public_key: publicKeyContent,
                    message: message,
                    signature: signature,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            document.getElementById("verify-result").innerText = JSON.stringify(data, null, 2);

            if (!data.valid) {
                alert(`Invalid Signature: ${data.error || 'Unknown error'}`);
            } else {
                alert("Valid Signature!");
            }
        } catch (error) {
            console.error("Error verifying signature:", error);
            document.getElementById("verify-result").innerText = `Error verifying signature: ${error.message}`;
        }
    };

    reader.onerror = function () {
        console.error("Error reading public key file.");
        alert("Error reading public key file.");
    };

    reader.readAsText(publicKeyFile);
}

// AES Encryption Functions
async function encryptText() {
    const password = document.getElementById("encrypt-password").value;
    const plaintext = document.getElementById("plaintext").value;
    
    if (!password || !plaintext) {
        alert("Please enter both password and text to encrypt.");
        return;
    }
    
    try {
        const response = await fetch('/aes_encrypt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                password: password,
                plaintext: plaintext
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        document.getElementById("encryption-result").innerText = JSON.stringify(data, null, 2);
        
        // Store encrypted data for download
        window.encryptedData = data;
        document.getElementById("download-encrypted").style.display = "block";
    } catch (error) {
        console.error("Error encrypting text:", error);
        document.getElementById("encryption-result").innerText = `Error encrypting text: ${error.message}`;
    }
}

function downloadEncryptedData() {
    if (window.encryptedData) {
        const blob = new Blob([JSON.stringify(window.encryptedData)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = "encrypted_data.json";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } else {
        alert("No encrypted data available.");
    }
}

function loadEncryptedFile() {
    const file = document.getElementById("encrypted-file").files[0];
    
    if (!file) {
        alert("Please select an encrypted file.");
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            document.getElementById("ciphertext").value = data.ciphertext || "";
            document.getElementById("salt").value = data.salt || "";
            document.getElementById("iv").value = data.iv || "";
        } catch (error) {
            console.error("Error parsing JSON file:", error);
            alert("Error parsing file. Is it a valid encrypted data file?");
        }
    };
    reader.readAsText(file);
}

async function decryptText() {
    const password = document.getElementById("decrypt-password").value;
    const ciphertext = document.getElementById("ciphertext").value;
    const salt = document.getElementById("salt").value;
    const iv = document.getElementById("iv").value;
    
    if (!password || !ciphertext || !salt || !iv) {
        alert("Please provide password, ciphertext, salt, and IV.");
        return;
    }
    
    try {
        const response = await fetch('/aes_decrypt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                password: password,
                ciphertext: ciphertext,
                salt: salt,
                iv: iv
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            document.getElementById("decryption-result").innerText = `Error: ${data.error}`;
        } else {
            document.getElementById("decryption-result").innerText = data.plaintext;
        }
    } catch (error) {
        console.error("Error decrypting text:", error);
        document.getElementById("decryption-result").innerText = `Error decrypting text: ${error.message}`;
    }
}