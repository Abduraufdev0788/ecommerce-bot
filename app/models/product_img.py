from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key = True)
    product_id =Column(Integer, ForeignKey('products.id', ondelete=('CASCADE'))) 
    image_url = Column(String(500), nullable=False)
    is_main = Column(Boolean, default=False)

    product = relationship("Product", back_populates="images",
    )
