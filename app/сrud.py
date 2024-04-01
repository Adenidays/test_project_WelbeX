from fastapi.params import Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Route, Point, RouteDB, PointDB


def save_route(db: Session, route: Route, points: list[Point]):
    db.add(route)
    db.commit()
    db.refresh(route)

    for point in points:
        point.route_id = route.id
        db.add(point)

    db.commit()


def get_route(db: Session, route_id: int):
    return db.query(Route).filter(Route.id == route_id).first()


def save_route_to_db(optimal_route: list[Point], db: Session = Depends(SessionLocal)):
    route_db = RouteDB()
    db.add(route_db)
    db.commit()
    db.refresh(route_db)

    for point in optimal_route:
        point_db = PointDB(lat=point.lat, lng=point.lng, route_id=route_db.id)
        db.add(point_db)

    db.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()