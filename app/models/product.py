from sqlalchemy import Column, String, BigInteger, Text, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


from app.models.base import Base

class Product(Base):

    __tablename__ = 'products'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(230), nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable= False)
    stock = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)

    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    category = relationship("Category", back_populates="products" )
    images = relationship( "ProductImage", back_populates="product",cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
