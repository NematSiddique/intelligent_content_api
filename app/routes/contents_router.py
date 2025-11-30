from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import SessionLocal
from app.database.models import Content, User
from app.database.schemas import ContentCreate, ContentResponse
from app.service.content_service import create_user_content, delete_user_content, get_all_user_contents, get_user_content
from app.service.user_service import get_current_user, verify_password, decode_access_token
from fastapi.security import OAuth2PasswordBearer
from app.service.analyze_sentiment import analyze_text  # async AI call
import logging
logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST /contents
@router.post("/", response_model=ContentResponse)
async def create_content(content: ContentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    response= await create_user_content(content, db, current_user)
    return response


# GET /contents
@router.get("/", response_model=List[ContentResponse])
def get_all_contents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    response= get_all_user_contents(db, current_user)
    return response


# GET /contents/{id}
@router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    response= get_user_content(content_id, db, current_user)
    return response


# DELETE /contents/{id}
@router.delete("/{content_id}")
def delete_content(content_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    response= delete_user_content(content_id, db, current_user)
    return response


@router.post("/analyze")
async def analyze_content(request: dict):
    """
    Analyze text for summary and sentiment using OpenAI GPT-3.5.
    Expects JSON: {"text": "your text here"}
    Returns JSON: {"summary": "...", "sentiment": "..."}
    """
    text = request.get("text", "").strip()
    logger.info(f"Analyzing text: {text}")
    if not text:
        logger.error("Text cannot be empty")
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    summary, sentiment = await analyze_text(text)
    logger.info(f"AI analysis complete. Summary: {summary}, Sentiment: {sentiment}")
    return {"summary": summary, "sentiment": sentiment}