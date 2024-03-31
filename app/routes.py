from fastapi import APIRouter, File, UploadFile, HTTPException
from models import Point, Route
from utils import calculate_optimal_route
import csv
import os

router = APIRouter()

MAX_FILE_SIZE_BYTES = 6291456  # 6 MB
MAX_ROWS_TO_READ = 3

routes = {}

@router.post("/routes", response_model=Route)
async def create_route(format: str = None, file: UploadFile = File(...)):
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

        route_id = len(routes) + 1
        routes[route_id] = optimal_route

        return {"id": route_id, "points": optimal_route}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/routes/{route_id}", response_model=Route)
async def get_route(route_id: int):
    if route_id not in routes:
        raise HTTPException(status_code=404, detail="Route not found")

    return {"id": route_id, "points": routes[route_id]}
