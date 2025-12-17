#
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.db import SessionLocal
from models.user import User
from models.question import Question
from schemas.questions import QuestionCreate, QuestionAnswer, QuestionForMe
from crypto.chek_token import get_current_user 

router = APIRouter(prefix="/questions", tags=["questions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Задать вопрос
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_question(
    question_data: QuestionCreate,  # ← Обрати внимание: есть ":"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверка получателя
    recipient = db.query(User).filter(User.id == question_data.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if current_user.id == question_data.recipient_id:
        raise HTTPException(status_code=400, detail="Cannot ask yourself")

    new_question = Question(
        sender_id=current_user.id,
        recipient_id=question_data.recipient_id,
        text=question_data.text
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return {"message": "Question sent", "question_id": new_question.id}

# 2. Мои входящие вопросы
@router.get("/my", response_model=List[QuestionForMe])
def get_my_questions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Question).filter(Question.recipient_id == current_user.id).all()

# 3. Ответить на вопрос
@router.put("/{question_id}/answer")
def answer_question(
    question_id: int,
    answer_data: QuestionAnswer,  # ← есть ":"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your question")
    if question.answer is not None:
        raise HTTPException(status_code=400, detail="Already answered")

    question.answer = answer_data.answer
    db.commit()
    return {"message": "Answer saved"}