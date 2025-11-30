from jose import JWTError
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from app.config import settings

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
