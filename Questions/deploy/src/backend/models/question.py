from sqlalchemy import Column, Integer, String, Text, DateTime
from database.db import Base
from datetime import datetime

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, index=True)
    text = Column(Text)
    answer = Column(Text, nullable=True)
    answered_at = Column(DateTime, nullable=True)