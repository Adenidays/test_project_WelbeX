# routes.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from models import Route, Point
from database import SessionLocal

router = APIRouter()

@router.post("/api/routes", response_model=Route)
async def create_route(format: str = None, file: UploadFile = File(...)):
    # Ваш код для чтения файла и создания маршрута

    db = SessionLocal()
    try:
        # Сохраняем точки в базе данных
        for point in points:
            db_point = Point(lat=point.lat, lng=point.lng)
            db.add(db_point)
            db.commit()
            db.refresh(db_point)

        # Сохраняем маршрут в базе данных
        db_route = Route(points=[db_point.id for db_point in db_points])
        db.add(db_route)
        db.commit()
        db.refresh(db_route)

        return db_route
    finally:
        db.close()
