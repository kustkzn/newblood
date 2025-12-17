from sqlalchemy import Column, Integer, String, ForeignKey
from database.db import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String(200), nullable=False)
    answer = Column(String(500), nullable=True)