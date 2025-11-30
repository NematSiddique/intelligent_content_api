from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import SessionLocal, get_db
from app.database.models import Content, User
from app.database.schemas import ContentCreate, ContentResponse
from app.service.user_service import get_current_user
from fastapi.security import OAuth2PasswordBearer
from app.service.analyze_sentiment import analyze_text  # async AI call
import logging
logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def create_user_content(content: ContentCreate, db: Session, current_user: User)-> ContentResponse:
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

def get_all_user_contents(db: Session, current_user: User) -> List[ContentResponse]:
    logger.info(f"Fetching all contents for user: {current_user.email}")
    results = (
    db.query(Content.id, Content.text)
    .filter(Content.user_id == current_user.id)
    .all()
    )
    logger.debug(f"Fetched contents: {results}")
    return results

def get_user_content(content_id: int, db: Session, current_user: User)-> ContentResponse:
    print("Current User",current_user)
    logger.info(f"Fetching content with ID {content_id} for user: {current_user.email}")
    content = db.query(Content).filter(Content.id == content_id, Content.user_id == current_user.id).first()
    logger.debug(f"Fetched content: {content}")
    if not content:
        logger.error(f"Content with ID {content_id} not found for user: {current_user.email}")
        raise HTTPException(status_code=404, detail="Content not found")
    return content


def delete_user_content(content_id: int, db: Session, current_user: User)-> dict:
    logger.info(f"Deleting content with ID {content_id} for user: {current_user.email}")
    content = db.query(Content).filter(Content.id == content_id, Content.user_id == current_user.id).first()
    if not content:
        logger.error(f"Content with ID {content_id} not found for user: {current_user.email}")
        raise HTTPException(status_code=404, detail="Content not found")
    db.delete(content)
    db.commit()
    return {"detail": "Content deleted successfully"}