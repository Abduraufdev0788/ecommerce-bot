from sqlalchemy import (
    Column, BigInteger, Numeric, DateTime,
    ForeignKey, Enum, func
)
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class OrderStatus(enum.Enum):
    YANGI = "YANGI"
    TOLANGAN = "TOLANGAN"
    YUBORILDI = "YUBORILDI"
    YAKUNLANDI = "YAKUNLANDI"
    BEKOR_QILINDI = "BEKOR_QILINDI"



class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    status = Column(
        Enum(OrderStatus, name="order_status"),
        nullable=False,
        default=OrderStatus.YANGI
    )

    total_price = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
