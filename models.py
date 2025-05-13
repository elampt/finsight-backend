from sqlalchemy import Column, Integer, String, ForeignKey, text, TIMESTAMP, Boolean, Float, Date
from sqlalchemy.orm import relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    # Relationship to Portfolio
    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")
    

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String, unique=True, index=True, nullable=False)
    stock_name = Column(String, nullable=False)
    sector = Column(String, nullable=False)

    # Relationship to Holdings
    holdings = relationship("Holding", back_populates="stock")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    shares = Column(Float, nullable=False)
    purchase_cost = Column(Float, nullable=False)
    purchase_date = Column(Date, nullable=False)

    # Relationship to User
    user = relationship("User", back_populates="holdings")
    stock = relationship("Stock", back_populates="holdings")

