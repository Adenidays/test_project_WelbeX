from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Point(BaseModel):
    lat: float
    lng: float

class Route(BaseModel):
    id: int
    points: list[Point]

class RouteDB(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_points = relationship("PointDB", back_populates="route")

class PointDB(Base):
    __tablename__ = 'points'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey('routes.id'))
    lat = Column(Float)
    lng = Column(Float)
    route = relationship("RouteDB", back_populates="route_points")
