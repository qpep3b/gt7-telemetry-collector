import sqlite3
import os
from uuid import uuid4
import time
from datetime import datetime
import shutil
import json
from sqlmodel import Session, create_engine, SQLModel, select

from src.domain.models import Car, Lap, Race, Track


class Storage():
    def __init__(self, storage_dir: str = '.run', verbose: bool = False):
        self._verbose = verbose
        self._storage_dir = storage_dir

        self._log("Инициализация хранилища")

        """
        Сохраняем телеметрию
        {storage_dir}/storage/_data/{session_id}/{lap_number}.csv
        """
        
        self.engine = create_engine(f"sqlite:///{self._storage_dir}/storage/db.sqlite")

        os.makedirs(f'{self._storage_dir}/storage/_data', exist_ok=True)
        self.db = sqlite3.connect(f'{self._storage_dir}/storage/db.sqlite')
        self.__init_tables()

        self._log("Хранилище создано")
    
    def __init_tables(self):
        SQLModel.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            self.__fill_cars(db)
            self.__fill_tracks(db)

    def create_session(self, car_id: int, best_lap_time: int) -> tuple[str, str]:
        session_id = uuid4().hex

        with Session(self.engine) as db:
            race = Race(
                id=session_id,
                car_id=car_id,
                best_lap_time=best_lap_time,
                end_ts=int(time.time())
            )
            db.add(race)
            db.commit()

        session_folder = f'{self._storage_dir}/storage/_data/{session_id}'
        os.makedirs(session_folder, exist_ok=True)
        self._log(f"Сессия {session_id} сохранена")
        return session_id, session_folder

    
    def save_lap(self, lap_number: int, race_id: str, lap_time: int):
        lap_id = uuid4().hex
        with Session(self.engine) as db:
            lap = Lap(
                id=lap_id,
                number=lap_number,
                race_id=race_id,
                time=lap_time,
            )
            db.add(lap)
            db.commit()
    
    def _log(self, msg: str):
        if self._verbose:
            print(f"[{datetime.now()}] {msg}")
    
    def _clear(self):
        shutil.rmtree(self._storage_dir)
    
    def __enter__(self):
        ...
    
    def __exit__(self):
        ...
    
    def get_all_laps(self):
        with Session(self.engine) as db:
            query = select(Lap)
            res = db.exec(query)
            laps = res.all()
        
        return laps
    
    def __fill_cars(self, db: Session):
        with open('data/cars.json') as f:
            cars_data = json.load(f)

        for car_data in cars_data.values():
            car = Car(
                id=int(car_data['id'][3:]),
                name=car_data['nameLong'],
                power=car_data['power_v'],
                torque=car_data['torque_v'],
                weight=car_data['weight_v'],
                length=car_data['length_v'],
                width=car_data['width_v'],
                height=car_data['height_v'],
                train=car_data['driveTrain'],
                class_=car_data['carClass'],
            )
            db.add(car)
            
        db.commit()
    
    def __fill_tracks(self, db: Session):
        with open('data/tracks.json') as f:
            tracks_data = json.load(f)

        for track_data in tracks_data.values():
            track = Track(
                name=track_data["nameLong"],
                length=track_data["length_v"],
                num_turns=track_data["cornerCount"],
                country=track_data["countryName"],
            )
            db.add(track)
        db.commit()