from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.auth.encryption import encrypt, decrypt
import os

router = APIRouter(prefix="/dev_test", tags=["test"])


class RawData(BaseModel):
    data: str


@router.post("/encrypt")
async def encrypt_data(body: RawData):
    try:
        encrypted = encrypt(body.data)
        return {"encrypted": encrypted}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/decrypt")
async def decrypt_data(body: RawData):
    try:
        decrypted = decrypt(body.data)
        return {"decrypted": decrypted}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Decryption failed")
