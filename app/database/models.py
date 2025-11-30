from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    contents = relationship("Content", back_populates="owner")

class Content(Base):
    __tablename__ = 'contents'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    text = Column(Text)
    summary = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)

    owner = relationship("User", back_populates="contents")
