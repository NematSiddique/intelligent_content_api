from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

try:
    with engine.connect() as conn:
        print("Connected successfully!")
except OperationalError as e:
    print("Connection failed:", e)
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()