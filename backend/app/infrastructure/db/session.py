from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings


def get_db():
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        yield session
