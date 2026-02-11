from sqlalchemy import Column, BigInteger, String, DateTime
from datetime import datetime

from app.models.base import Base

class Categorie(Base):

    __tablename__ = 'categories'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(230), nullable=False)
    created_at = Column(DateTime(timezone=True),default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)
