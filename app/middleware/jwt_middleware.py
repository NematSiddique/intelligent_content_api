from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request
from jose import JWTError, ExpiredSignatureError
from starlette.types import ASGIApp, Receive, Scope, Send
from app.database.database import SessionLocal
from app.database.models import User
from app.service.user_service import decode_access_token
import logging
logger = logging.getLogger(__name__)

class JWTMiddleware:
  
  def __init__(self, app: ASGIApp):
    self.app = app

  async def __call__(self, scope: Scope, receive: Receive, send: Send):
    if scope["type"] != "http":

      await self.app(scope, receive, send)
      return

    request = Request(scope, receive=receive)

    if request.method == "OPTIONS":
      await self.app(scope, receive, send)
      return

    path = scope["path"]
    if path in [
    "/intelligent_content_api/v1/users/login",
    "/intelligent_content_api/v1/users/signup",
    "/intelligent_content_api/v1/openapi.json",
    "/docs",]:
      await self.app(scope, receive, send)

      return

    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
      response = JSONResponse(
        status_code=401,
        content={"detail": "Authorization token missing or invalid."}
      )
      await response(scope, receive, send)
      return
    
    token = token.split(" ")[1]

    try:
      payload = decode_access_token(token)
      
      user_id = payload.get("id")  

      logger.debug(f"Decoded token payload: {payload}")
      if not user_id:
          logger.error("User ID not found in token payload")
          raise HTTPException(status_code=401, detail="Invalid token")
      db = SessionLocal() 
      user = db.query(User).filter(User.id == user_id).first()
      logger.debug(f"Fetched user from DB: {user}")
      if not user:
          logger.error("User not found in database")
          raise HTTPException(status_code=404, detail="User not found")
      request.state.user = user
    
    except HTTPException as e:
      response = JSONResponse(
        status_code=e.status_code,
        content={"detail": e.detail},
      )
      await response(scope, receive, send)
      return
    except ExpiredSignatureError:
      response = JSONResponse(
        status_code=401,
        content={"detail": "Token has expired"},
      )
      await response(scope, receive, send)
      return
    except JWTError:
      response = JSONResponse(
      status_code=401,
      content={"detail": "Invalid token"},)

      await response(scope, receive, send)
      return
    await self.app(scope, receive, send)