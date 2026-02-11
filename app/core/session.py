from app.core.database import engine
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(engine)
