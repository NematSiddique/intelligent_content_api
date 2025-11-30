from fastapi import Depends, HTTPException, Request, status
from jose import ExpiredSignatureError, JWTError
from passlib.context import CryptContext
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
from app.config import settings
import logging

from app.database.database import get_db
from app.database.models import User
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


bearer_scheme = HTTPBearer(description="Enter your JWT Bearer token")

async def get_token_header(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    return token

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
        return payload
    except ExpiredSignatureError as e:
        # Re-raise the specific exception you want to catch in the middleware
        raise ExpiredSignatureError("Token has expired") from e
    except JWTError as e:
        # Re-raise the specific exception you want to catch in the middleware
        raise JWTError("Invalid token") from e
    
def create_token(data: dict):
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXP_MINUTES)
    payload["exp"] = expire
    payload["iat"] = datetime.utcnow()
    payload["nbf"] = datetime.utcnow()
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)

def get_current_user(request: Request) -> User:
    if not hasattr(request.state, "user") or request.state.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: user not found in request",
        )
    
    user = request.state.user
    return user