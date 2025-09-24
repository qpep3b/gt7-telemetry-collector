import sqlite3
import os
from uuid import uuid4
import time
from datetime import datetime


class Storage():
    def __init__(self, verbose: bool = False):
        self._verbose = verbose

        self._log("Инициализация хранилища")

        """
        Сохраняем телеметрию
        ./run/storage/_data/{session_id}/{lap_number}.csv
        """
        
        os.makedirs('.run/storage/_data', exist_ok=True)
        self.db = sqlite3.connect('.run/storage/db.sqlite')
        self.__init_tables()

        self._log("Хранилище создано")
    
    def __init_tables(self):
        cursor = self.db.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                track_id INTEGER,
                car_id INTEGER,
                racer INTEGER,
                best_lap_time INTEGER,
                end_ts INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laps (
                id TEXT PRIMARY KEY,
                number INTEGER,
                race_id INTEGER,
                time INTEGER
            )
        """)

        cursor.close()

    def create_session(self, car_id: int, best_lap_time: int) -> str:
        session_id = uuid4().hex

        cursor = self.db.cursor()
        cursor.execute(
            """
                INSERT INTO sessions (id, car_id, best_lap_time, end_ts)
                VALUES (?, ?, ?, ?)
            """,
            (
                session_id, car_id, best_lap_time, int(time.time())
            )
        )
        cursor.close()

        self._log(f"Сессия {session_id} сохранена")

    
    def save_lap(self, lap_number: int, race_id: str, lap_time: int):
        lap_id = uuid4().hex
        cursor = self.db.cursor()
        cursor.execute(
            """
                INSERT INTO laps (id, number, race_id, time)
                VALUES (?, ?, ?, ?)
            """,
            (
                lap_id, lap_number, race_id, lap_time
            )
        )
        cursor.close()
    
    def _log(self, msg: str):
        if self._verbose:
            print(f"[{datetime.now()}] {msg}")
    
    def __enter__(self):
        ...
    
    def __exit__(self):
        ...