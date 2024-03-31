from itertools import permutations
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import csv
import os

app = FastAPI()

MAX_FILE_SIZE_BYTES = 6291456  # 6 MB
MAX_ROWS_TO_READ = 3


class Point(BaseModel):
    lat: float
    lng: float


class Route(BaseModel):
    id: int
    points: List[Point]


routes = {}


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


@app.post("/api/routes", response_model=Route)
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


@app.get("/api/routes/{route_id}", response_model=Route)
async def get_route(route_id: int):
    if route_id not in routes:
        raise HTTPException(status_code=404, detail="Route not found")

    return {"id": route_id, "points": routes[route_id]}
