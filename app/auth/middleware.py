from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.auth.encryption import decrypt, encrypt
from app.core.config import settings


class EncryptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for AES-CBC encrypted request/response bodies.
    Decrypts incoming text/plain requests; encrypts JSON responses.
    """

    async def dispatch(self, request: Request, call_next):
        if not settings.ENCRYPTION_ENABLED or request.url.path in settings.ENCRYPTION_EXCLUDED_PATHS:
            return await call_next(request)

        if request.method in ("POST", "PUT", "PATCH") and request.headers.get("content-type") == "text/plain":
            try:
                raw_body = await request.body()
                decrypted = decrypt(raw_body.decode())
                request._body = decrypted.encode()
            except Exception:
                return Response("Decryption failed", status_code=400)

        response = await call_next(request)

        if response.headers.get("content-type") == "application/json":
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            encrypted_body = encrypt(body.decode())
            return Response(content=encrypted_body, media_type="text/plain")

        return response
