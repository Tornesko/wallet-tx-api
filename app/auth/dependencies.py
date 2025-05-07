from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.jwt import decode_access_token

oauth2_scheme = HTTPBearer()


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_access_token(token.credentials)
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
