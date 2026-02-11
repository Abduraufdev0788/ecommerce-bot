from sqlalchemy import (
    Column, BigInteger, Integer, Numeric,
    DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.models.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True)

    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    items = relationship("OrderItem", back_populates="order")
