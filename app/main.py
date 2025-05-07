from fastapi import FastAPI
from app.api import router
from app.auth.middleware import EncryptionMiddleware

app = FastAPI()
app.include_router(router)
app.add_middleware(EncryptionMiddleware)
