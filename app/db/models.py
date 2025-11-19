from sqlalchemy import Column, Integer, String, Boolean
from .database import Base  # use the same Base

# -------------------
# Product Model
# -------------------
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Integer, default=0)
    active = Column(Boolean, default=True)


# -------------------
# Webhook Model
# -------------------
class Webhook(Base):
    __tablename__ = "webhooks"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # <- match DB column
    enabled = Column(Boolean, default=True)
