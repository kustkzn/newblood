# routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import SessionLocal
from models.user import User
from models.question import Question
from schemas.user import UserPublic, UserPublicWithQuestions

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ (без вопросов) ===
@router.get("/", response_model=List[UserPublic])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# === ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ + ВОПРОСЫ, ЗАДАННЫЕ ЕМУ ===
@router.get("/{user_id}", response_model=UserPublicWithQuestions)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    questions = db.query(Question).filter(Question.recipient_id == user.id).all()

    return {
        "id": user.id,
        "username": user.username,
        "questions_received": questions
    }