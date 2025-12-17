# schemas/user.py
from pydantic import BaseModel
from typing import List, Optional

class QuestionPublic(BaseModel):
    id: int
    text: str
    answer: Optional[str] = None

    class Config:
        from_attributes = True

class UserPublicWithQuestions(BaseModel):
    id: int
    username: str

    questions_received: List[QuestionPublic]  

    class Config:
        from_attributes = True

class UserPublic(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True