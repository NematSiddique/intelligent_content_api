from fastapi.responses import JSONResponse
from fastapi import Request
from jose import JWTError, ExpiredSignatureError
from starlette.types import ASGIApp, Receive, Scope, Send

from app.service.auth_service import decode_access_token

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
    "/users/signin",
    "/users/signup",
    "/openapi.json",
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
      request.state.user = payload
    
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