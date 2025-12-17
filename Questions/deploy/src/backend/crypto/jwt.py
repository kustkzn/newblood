import os
import time
import uuid
from jose import jwt, JWTError


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(user_id: int) -> tuple[str, str, int]:
    jti = str(uuid.uuid4())          # уникальный ID токена
    iat = int(time.time())           # текущее время в секундах
    exp = iat + 60 * ACCESS_TOKEN_EXPIRE_MINUTES

    payload = {
        "sub": str(user_id),         # ID пользователя
        "jti": jti,
        "iat": iat,
        "exp": exp,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, iat

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None