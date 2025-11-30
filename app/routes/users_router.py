import re
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User
from app.database.schemas import UserCreate, UserLogin, UserResponse
from app.service.user_service import create_token, hash_password, verify_password
import logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(data: UserCreate, db: Session = Depends(get_db)):

    # check existing user
    existing = db.query(User).filter(User.email == data.email).first()
    
    if existing:
        logger.error(f"User already exists with email: {data.email}")
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Password regex rule
    password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

    # validate raw password
    if not re.match(password_pattern, data.password):
        logger.error("Password does not meet complexity requirements")
        raise HTTPException(status_code=400, detail=("Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character."))
    
    hashed_password = hash_password(data.password)
    new_user = User(email=data.email, password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user created: {new_user.email}")

    return new_user


@router.post("/login")
def signin(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        logger.error(f"Invalid credentials for email: {data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"id": user.id, "email": user.email})
    logger.info(f"User signed in: {user.email}")
    return {"access_token": token, "token_type": "bearer"}
