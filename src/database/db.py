from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
