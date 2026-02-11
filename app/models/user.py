from sqlalchemy.orm import relationship
from sqlalchemy import String, Column, BigInteger, DateTime

from app.models.base import Base

class User(Base):

    __tablename__ = 'users'


    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    phone_number = Column(String(20))
    fullname = Column(String(150), nullable= False)

    orders = relationship( "Order", back_populates="user")
