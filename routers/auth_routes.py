from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth

router = APIRouter(prefix = "/auth", tags = ["authentication"])

@router.post("/register", response_model = schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code = 400, detail = "Username already exists")
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code = 400, detail = "Email already exists")
    new_user = models.User(
        username = user.username,
        email = user.email,
        hashed_password = auth.hash_password(user.password),
        role = "user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model = schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code = 401, detail = "Invalid username or password")
    token = auth.create_access_token(data = {"sub" : db_user.username , "role" : db_user.role})
    return {"access_token" : token, "token_type" : "bearer"}