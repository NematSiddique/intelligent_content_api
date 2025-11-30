from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import SessionLocal
from app.database.models import Content, User
from app.database.schemas import ContentCreate, ContentListResponse, ContentResponse
from app.service.content_service import create_user_content, delete_user_content, get_all_user_contents, get_user_content
from app.service.user_service import get_current_user, get_token_header
from app.service.analyze_sentiment import analyze_text  # async AI call
import logging
logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST /contents
@router.post("/", response_model=ContentResponse)
async def create_content(content: ContentCreate,token: str = Depends(get_token_header), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        response= await create_user_content(content, db, current_user)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating content: {e}")
        raise e


# GET /contents
@router.get("/", response_model=List[ContentListResponse])
def get_all_contents(token: str = Depends(get_token_header),db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        response= get_all_user_contents(db, current_user)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching all contents: {e}")
        raise HTTPException(status_code=500, detail="Error fetching contents")

# GET /contents/{id}
@router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: int,token: str = Depends(get_token_header), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        response= get_user_content(content_id, db, current_user)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching content with id {content_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching content")

# DELETE /contents/{id}
@router.delete("/{content_id}")
def delete_content(content_id: int,token: str = Depends(get_token_header), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        response= delete_user_content(content_id, db, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting content with id {content_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting content")
    return response