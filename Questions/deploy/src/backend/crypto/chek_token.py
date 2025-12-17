# auth/dependencies.py
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import SessionLocal
from models.user import User
from jwt import decode_token

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    jti = payload.get("jti")
    iat = payload.get("iat")

    if not user_id or not jti or not iat:
        raise HTTPException(status_code=401, detail="Token missing required fields")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if user.active_session_jti != jti or user.session_created_at != iat:
        raise HTTPException(status_code=401, detail="Session revoked or expired")

    return user