from fastapi import Depends, HTTPException
from jose import JWTError
from passlib.context import CryptContext
import jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from app.config import settings
from sqlalchemy.orm import Session
import logging

from app.database.database import get_db
from app.database.models import User
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
        print("JWT secret at decode:", settings.JWT_SECRET)
        return payload
    except JWTError as e:
        raise e
    
def create_token(data: dict):
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXP_MINUTES)
    payload["exp"] = expire
    payload["iat"] = datetime.utcnow()
    payload["nbf"] = datetime.utcnow()
    print("JWT secret at encode:", settings.JWT_SECRET)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("id")  # make sure your JWT contains this key
        logger.debug(f"Decoded token payload: {payload}")
        if not user_id:
            logger.error("User ID not found in token payload")
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token decoding error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    logger.debug(f"Fetched user from DB: {user}")
    if not user:
        logger.error("User not found in database")
        raise HTTPException(status_code=404, detail="User not found")
    return user