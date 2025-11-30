import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.models import Content, User
from app.database.schemas import ContentCreate, ContentListResponse, ContentResponse
from fastapi.security import OAuth2PasswordBearer
from app.service.analyze_sentiment import analyze_text  # async AI call
from app.caching.redis import redis_client

import logging
from app.config import settings
logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
CACHE_KEY = "contents_cache"
CACHE_TTL = settings.REDIS_CACHE_TTL  # default = 60 seconds

async def create_user_content(content: ContentCreate, db: Session, current_user: User)-> ContentResponse:
    logger.info(f"Creating content for user: {current_user.email}")
    
    try:
        # Basic validation
        if not content.text or len(content.text.strip()) == 0:
            logger.error("Content text is empty")
            raise HTTPException(status_code=400, detail="Content text cannot be empty")
    
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
        cache_key = f"user_contents:{current_user.id}"
        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    logger.debug("Deleting contents from Redis cache")
                    # Convert JSON string back into list of dicts
                    redis_client.delete(f"user_contents:{current_user.id}")
            except Exception as e:
                logger.error(f"Redis read error: {e}")
        
        logger.info(f"Content updated with AI analysis: {new_content}")
        db.refresh(new_content)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user content for user: {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating content for user: {current_user.email}")
    logger.debug(f"Created content : {new_content} for user: {current_user.email}")
    return new_content

def get_all_user_contents(db: Session, current_user: User) -> List[ContentListResponse]:
    logger.info(f"Fetching all contents for user: {current_user.email}")
    cache_key = f"user_contents:{current_user.id}"
    # Try cache first
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.debug("Serving contents from Redis cache")
                # Convert JSON string back into list of dicts
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Redis read error: {e}")

    # Fallback to DB
    try:
        results = (
            db.query(Content.id, Content.text)
            .filter(Content.user_id == current_user.id)
            .all()
        )
        response = [{"id": r[0], "text": r[1]} for r in results]
    except Exception as e:
        logger.error(f"Error fetching user contents for user: {current_user.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching contents for user: {current_user.email}",
        )

    logger.debug(f"Fetched contents from DB: {results}")

    # Cache it
    if redis_client:
        try:
            logger.debug("Caching contents in Redis")
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(response))
        except Exception as e:
            logger.error(f"Redis write error: {e}")
    return results

def get_user_content(content_id: int, db: Session, current_user: User)-> ContentResponse:
    logger.info(f"Fetching content with ID {content_id} for user: {current_user.email}")
    try:
      content = db.query(Content).filter(Content.id == content_id, Content.user_id == current_user.id).first()
      if not content:
          logger.error(f"Content with ID {content_id} not found for user: {current_user.email}")
          raise HTTPException(status_code=404, detail="Content not found")
    except HTTPException:
      raise
    except Exception as e:
      logger.error(f"Error fetching user content with ID {content_id} for user: {current_user.email}: {e}")
      raise HTTPException(status_code=500, detail=f"Error fetching content with ID {content_id} for user: {current_user.email}")
    logger.debug(f"Fetched content: {content} for user: {current_user.email}")
    return content


def delete_user_content(content_id: int, db: Session, current_user: User)-> dict:
    logger.info(f"Deleting content with ID {content_id} for user: {current_user.email}")
    try:
      content = db.query(Content).filter(Content.id == content_id, Content.user_id == current_user.id).first()
      if not content:
          logger.error(f"Content with ID {content_id} not found for user: {current_user.email}")
          raise HTTPException(status_code=404, detail="Content not found")
      db.delete(content)
      db.commit()
      cache_key = f"user_contents:{current_user.id}"
      if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    logger.debug("Deleting contents from Redis cache")
                    # Convert JSON string back into list of dicts
                    redis_client.delete(f"user_contents:{current_user.id}")
            except Exception as e:
                logger.error(f"Redis read error: {e}")
    except HTTPException:
      raise
    except Exception as e:
      logger.error(f"Error deleting user content with ID {content_id} for user: {current_user.email}: {e}")
      raise HTTPException(status_code=500, detail=f"Error deleting content with ID {content_id} for user: {current_user.email}")
    logger.debug(f"Deleted content with ID {content_id} for user: {current_user.email}")
    return {"detail": "Content deleted successfully"}