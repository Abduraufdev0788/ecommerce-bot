from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL



DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.DB_USER,
    password=settings.DB_PASS,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME
)

engine = create_engine(DATABASE_URL)
