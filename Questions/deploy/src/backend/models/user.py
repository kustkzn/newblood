from sqlalchemy import Column, Integer, String
from database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False) 
    keyword = Column(String(50), nullable=False)

    active_session_jti = Column(String(36), nullable=True) 
    session_created_at = Column(Integer, nullable=True) 