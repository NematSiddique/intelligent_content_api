from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import SessionLocal
from app.database.models import Content, User
from app.database.schemas import ContentCreate, ContentResponse
from app.service.auth_service import verify_password, decode_access_token
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


# Get current user
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


# POST /contents
@router.post("/", response_model=ContentResponse)
async def create_content(content: ContentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Creating content for user: {current_user.email}")
    logger.debug(f"Raw content: {content.text}")
    # Save content first
    new_content = Content(user_id=current_user.id, text=content.text, summary=None, sentiment=None)
    db.add(new_content)
    db.commit()
    db.refresh(new_content)

    # Async call to AI to get summary & sentiment
    summary, sentiment = await analyze_text(content.text)
    logger.info(f"AI analysis complete. Summary: {summary}, Sentiment: {sentiment}")

    # Update DB record with AI results
    new_content.summary = summary
    new_content.sentiment = sentiment
    db.commit()
    logger.info(f"Content updated with AI analysis: {new_content}")
    db.refresh(new_content)


    return new_content


# GET /contents
@router.get("/", response_model=List[ContentResponse])
def get_all_contents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Fetching all contents for user: {current_user.email}")
    contents = db.query(Content).filter(Content.user_id == current_user.id).all()
    logger.debug(f"Fetched contents: {contents}")
    return contents


# GET /contents/{id}
@router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Fetching content with ID {content_id} for user: {current_user.email}")
    content = db.query(Content).filter(Content.id == content_id, Content.user_id == current_user.id).first()
    logger.debug(f"Fetched content: {content}")
    if not content:
        logger.error(f"Content with ID {content_id} not found for user: {current_user.email}")
        raise HTTPException(status_code=404, detail="Content not found")
    return content


# DELETE /contents/{id}
@router.delete("/{content_id}")
def delete_content(content_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Deleting content with ID {content_id} for user: {current_user.email}")
    content = db.query(Content).filter(Content.id == content_id, Content.user_id == current_user.id).first()
    if not content:
        logger.error(f"Content with ID {content_id} not found for user: {current_user.email}")
        raise HTTPException(status_code=404, detail="Content not found")
    db.delete(content)
    db.commit()
    return {"detail": "Content deleted successfully"}


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