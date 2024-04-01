from fastapi import File, UploadFile, HTTPException, Depends, APIRouter
from sqlalchemy.orm import  Session
import csv

from models import Route, Point, RouteDB
from utils import calculate_optimal_route
from сrud import save_route_to_db, get_db

router = APIRouter()


@router.post("/api/routes", response_model=Route)
async def create_route(format: str = None, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if format != 'csv':
        raise HTTPException(status_code=400, detail="Only CSV format is supported")

    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")


    try:
        contents = await file.read()
        contents = contents.decode("utf-8").splitlines()

        points = []
        field_count = 0
        for line in csv.reader(contents):

            if field_count == 0:
                field_count += 1
                continue
            lat, lng = map(float, line[1:3])
            points.append(Point(lat=lat, lng=lng))
            field_count += 1

        optimal_route = calculate_optimal_route(points)

        save_route_to_db(db, optimal_route)

        route_id = 1
        return {"id": route_id, "points": optimal_route}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/routes/{route_id}", response_model=Route)
async def get_route(route_id: int, db: Session = Depends(get_db)):
    route_db = db.query(RouteDB).filter(RouteDB.id == route_id).first()
    if not route_db:
        raise HTTPException(status_code=404, detail="Route not found")

    points_db = route_db.route_points
    points = [Point(lat=point_db.lat, lng=point_db.lng) for point_db in points_db]

    return {"id": route_id, "points": points}
