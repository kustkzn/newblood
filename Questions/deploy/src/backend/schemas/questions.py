from pydantic import BaseModel
from typing import Optional

class QuestionCreate(BaseModel):
    recipient_id: int
    text: str

class QuestionAnswer(BaseModel):
    answer: str

class QuestionForMe(BaseModel):
    id: int
    recipient_id: int
    text: str
    answer: Optional[str] = None

    class Config:
        from_attributes = True