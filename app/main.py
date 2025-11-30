from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.jwt_middleware import JWTMiddleware
from app.routes import contents_router, users_router
from app.database.database import Base, engine
from app.logging_config import setup_logging

# Create all DB tables
Base.metadata.create_all(bind=engine)
setup_logging()
app = FastAPI(
    title="Intelligent Content API",
    description="LLM-powered summary + sentiment service with JWT auth",
    version="1.0.0"
)

# CORS (feel free to restrict this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(JWTMiddleware)

# Routers
app.include_router(users_router.router, prefix="/users", tags=["Users"])
app.include_router(contents_router.router, prefix="/contents", tags=["Contents"])

@app.get("/")
def root():
    return {"message": "Intelligent Content API is running"}
