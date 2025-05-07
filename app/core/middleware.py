from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.auth.encryption import decrypt, encrypt
from app.core.config import ENCRYPTION_ENABLED


class EncryptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for AES-CBC encrypted request/response bodies.

    Required by spec: all data must be end-to-end encrypted.
    Decrypts incoming text/plain requests; encrypts JSON responses.
    """

    async def dispatch(self, request: Request, call_next):
        if not ENCRYPTION_ENABLED:
            return await call_next(request)
        if request.url.path.startswith("/docs") \
                or request.url.path.startswith("/openapi.json") \
                or request.url.path.startswith("/auth/login") or request.url.path.startswith("/dev_test/"):
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
