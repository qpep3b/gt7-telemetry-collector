from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, select, desc
from src.domain.models import Car, Track, Race, Lap


# ToDo: Переиспользовать из src
db_url = "sqlite:///.run/storage/db.sqlite"
connect_args = {"check_same_thread": False}
engine = create_engine(db_url, connect_args=connect_args)

def get_db():
    with Session(engine) as session:
        yield session

app = FastAPI()


@app.get("/tracks")
def get_tracks_list(db: Session = Depends(get_db)):
    query = select(Track).order_by(Track.name)
    res = db.execute(query).scalars().all()
    return res


@app.get("/cars")
def get_sessions_list(db: Session = Depends(get_db)):
    query = select(Car).order_by(Car.id)
    res = db.execute(query).scalars().all()
    return res


@app.get("/cars/{car_id}")
def get_car_detail(car_id: str, db: Session = Depends(get_db)):
    query = select(Car).where(Car.id == car_id)
    res = db.execute(query).scalar_one_or_none()
    return res


@app.get("/sessions")
def get_sessions_list(db: Session = Depends(get_db)):
    query = select(Race).order_by(desc(Race.end_ts))
    res = db.execute(query).scalars().all()
    return res


@app.get("/sessions/{session_id}/laps")
def get_session_laps_list(session_id: str, db: Session = Depends(get_db)):
    query = select(Lap).where(Lap.race_id == session_id).order_by(Lap.number)
    res = db.execute(query).scalars().all()
    return res
