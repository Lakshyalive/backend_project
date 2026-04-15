from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    username = Column(String, unique = True, index = True, nullable = False)
    email = Column(String, unique = True, index = True, nullable = False)
    hashed_password = Column(String, nullable = False)
    role = Column(String, default = "user", nullable = False)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    description = Column(String, default = "")
    completed = Column(Boolean, default = False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable = False)

