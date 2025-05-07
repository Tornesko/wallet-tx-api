import json
import os
import base64
import hmac
import hashlib
from functools import wraps
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

from app.core.config import ENCRYPTION_ENABLED

KEY = os.getenv("AES_PASSPHRASE", "").encode()

if len(KEY) not in (16, 24, 32):
    raise ValueError("AES_PASSPHRASE must be 16, 24, or 32 bytes")

BLOCK_SIZE = 128  # for PKCS7 padding (in bits)


def encrypt(plaintext: str) -> str:
    iv = os.urandom(16)
    padder = PKCS7(BLOCK_SIZE).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    hmac_digest = hmac.new(KEY, ciphertext, hashlib.sha256).digest()
    return base64.b64encode(iv + hmac_digest + ciphertext).decode()


def decrypt(encoded_ciphertext: str) -> str:
    try:
        raw = base64.b64decode(encoded_ciphertext)
        iv = raw[:16]
        hmac_received = raw[16:48]
        ciphertext = raw[48:]

        hmac_expected = hmac.new(KEY, ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(hmac_received, hmac_expected):
            raise ValueError("HMAC mismatch")

        cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = PKCS7(BLOCK_SIZE).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext.decode()
    except Exception:
        raise ValueError("Decryption failed")
