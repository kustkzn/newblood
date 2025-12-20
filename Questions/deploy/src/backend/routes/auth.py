# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.auth import UserRegister, UserLogin, Token, UserPublic
from models.user import User
from crypto.myjwt import get_password_hash, verify_password, create_access_token
from crypto.chek_token import get_db, get_current_user

router = APIRouter(tags=["auth"])

# === РЕГИСТРАЦИЯ ===
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pw = get_password_hash(data.password)
    
    new_user = User(
        username=data.username,
        hashed_password=hashed_pw,
        keyword=data.keyword
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}

# === ВХОД (LOGIN) ===
@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token, jti, iat = create_access_token(user.id)
    user.active_session_jti = jti
    user.session_created_at = iat
    db.commit()

    return {"access_token": token, "token_type": "bearer"}

# === ВЫХОД (LOGOUT) ===
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.active_session_jti = None
    current_user.session_created_at = None
    db.commit()
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserPublic)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user