from itertools import permutations

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import csv
import os

DATABASE_URL = "postgresql://username:password@db/nudges"

Base = declarative_base()

app = FastAPI()

MAX_FILE_SIZE_BYTES = 6291456  # 6 MB
MAX_ROWS_TO_READ = 3


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


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_optimal_route(points):
    all_permutations = permutations(points[1:])
    optimal_route = []
    min_distance = float('inf')

    for perm in all_permutations:
        total_distance = 0
        current_point = points[0]
        for point in perm:
            total_distance += ((current_point.lat - point.lat) ** 2 + (current_point.lng - point.lng) ** 2) ** 0.5
            current_point = point
        total_distance += ((current_point.lat - points[0].lat) ** 2 + (current_point.lng - points[0].lng) ** 2) ** 0.5

        if total_distance < min_distance:
            min_distance = total_distance
            optimal_route = [points[0]] + list(perm) + [points[0]]

    return optimal_route


def save_route_to_db(db: Session, optimal_route):
    route_db = RouteDB()
    db.add(route_db)
    db.commit()
    db.refresh(route_db)

    for point in optimal_route:
        point_db = PointDB(lat=point.lat, lng=point.lng, route_id=route_db.id)
        db.add(point_db)

    db.commit()


@app.post("/api/routes", response_model=Route)
async def create_route(format: str = None, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if format != 'csv':
        raise HTTPException(status_code=400, detail="Only CSV format is supported")

    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    if os.fstat(file.file.fileno()).st_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File size should not exceed 6 MB")

    try:
        contents = await file.read()
        contents = contents.decode("utf-8").splitlines()

        points = []
        field_count = 0
        for line in csv.reader(contents):
            if field_count >= MAX_ROWS_TO_READ:
                break
            if field_count == 0:
                field_count += 1
                continue
            lat, lng = map(float, line[1:3])
            points.append(Point(lat=lat, lng=lng))
            field_count += 1

        optimal_route = calculate_optimal_route(points)

        save_route_to_db(db, optimal_route)

        route_id = 1  # Assuming route_id incrementation, adjust this as per your actual logic
        return {"id": route_id, "points": optimal_route}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/routes/{route_id}", response_model=Route)
async def get_route(route_id: int, db: Session = Depends(get_db)):
    route_db = db.query(RouteDB).filter(RouteDB.id == route_id).first()
    if not route_db:
        raise HTTPException(status_code=404, detail="Route not found")

    points_db = route_db.route_points
    points = [Point(lat=point_db.lat, lng=point_db.lng) for point_db in points_db]

    return {"id": route_id, "points": points}
