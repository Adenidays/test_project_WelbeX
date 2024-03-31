from pydantic import BaseModel
from typing import List

class Point(BaseModel):
    lat: float
    lng: float

class Route(BaseModel):
    id: int
    points: List[Point]
