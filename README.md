## Getting Started

1. Copy the example environment file:

    ```bash
    cp .env.default .env
    ```

2. Build and start the project using Docker Compose:

    ```bash
    docker-compose up --build
    ```
    

Отлично, вот лаконичная английская версия `README.md`, адаптированная под Postman и реальное использование:

---

## Auth & Encryption

### Authentication

* Uses JWT.
* Get token:

  ```http
  POST /auth/login
  {
    "username": "admin",
    "password": "secret"
  }
  ```
* Use in headers:

  ```
  Authorization: Bearer <TOKEN>
  ```

---

### AES Encryption (CBC + HMAC)

All request and response bodies are encrypted using AES-CBC with HMAC.
Encryption is applied to:

* `POST`, `PUT`, `PATCH` request bodies (`Content-Type: text/plain`)
* all JSON responses (returned as base64)

---

### Disable Encryption (for Swagger/Postman)

In `.env`:

```env
ENCRYPTION_ENABLED=false
```

* Disables encryption middleware and decorators
* Allows testing with raw JSON
* Swagger UI works normally

---
