# routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import SessionLocal
from models.user import User
from models.question import Question
from schemas.user import UserPublic, UserPublicWithQuestions
from crypto.enc import spesial_encrypt

router = APIRouter(tags=["users"])

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
@router.get("/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем ВСЕ входящие вопросы (включая отвеченные и неотвеченные)
    questions = db.query(Question).filter(Question.recipient_id == user.id).all()

    # 🔒 Применяем одностороннее преобразование ТОЛЬКО к неотвеченным вопросам
    masked_questions = []
    for q in questions:
        masked_q = {
            "id": q.id,
            "recipient_id": q.recipient_id,
            "answer": q.answer,
            "answered_at": q.answered_at
        }
        if q.answer is None:
            # Нет ответа → маскируем текст
            masked_q["text"] = spesial_encrypt(q.text, user.keyword)
        else:
            # Есть ответ → оставляем исходный текст
            masked_q["text"] = q.text
        masked_questions.append(masked_q)

    return {
        "id": user.id,
        "username": user.username,
        "questions_received": masked_questions
    }

@router.get("/{user_id}/questions")
def get_user_sent_questions(user_id: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.sender_id == user_id).all()
    return questions