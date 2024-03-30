# models.py
from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import relationship
from database import Base

class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float)
    lng = Column(Float)

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    points = relationship("Point", back_populates="route")
