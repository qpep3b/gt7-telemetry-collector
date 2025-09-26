import enum
from typing import Optional
from src.schema.telemetry import TelemetryStat

from src.services.lap import LapTracker
from src.storage import Storage


class RaceType(enum.Enum):
    RACE = 0
    TIME_TRIAL = 1
    REPLAY = 2


class RaceTracker:
    def __init__(self, race_type: RaceType):
        self.max_speed = -1
        self.cur_lap_idx = -1
        self.laps: list[LapTracker] = []
        self.car_id: Optional[int] = None
        self.special_packet_time = 0.0

        self._prev_event: Optional[TelemetryStat] = None
        self._best_lap = None
        self.race_type = race_type
    
    def _is_new_lap(self, event: TelemetryStat) -> bool:
        if event.current_lap <= 0:
            return False

        # В случае тайм триала у нас нет total_laps
        # В случае просмотра демонстрации in_race != true
        # Надо уметь разделять режимы

        """
            Гонка:
                in_race: true
                есть total_laps (хотя надо посмотреть гонки на выносливость)

                Начало: current_lap = 1 (prev_lap = 0)
                Конец гонки = current_lap > total_laps
            Тайм триал
                in_race: true
                current_position: -1
                total_laps: -1

                Начало первого круга -- current_lap = 1 (prev_lap = 0)
                Конец -- in_race: false, последний круг не учитываем
            Повтор (квала или тайм триал)
                in_race: false
                current_position: 1
                total_laps: 1

                Начало круга -- current_lap = 1 (prev_lap = 0)
                Конец -- current_lap = 2
            Демонстрация (учебный центр или знакомство с трассами)
                Пока не делаю

            Есть глюк когда
        """
        if self._prev_event is None and event.current_lap > 0:
            return True
        
        if event.current_lap > self._prev_event.current_lap:
            return True
        
        return False

    def process_event(self, event: TelemetryStat):
        if self.car_id is None:
            self.car_id = event.car_id

        if len(self.laps) == 0:
            self.special_packet_time = 0

        if self._is_new_lap(event):
            self.special_packet_time += event.last_lap - len(self.laps) * 1000 / 60
            if self.laps:
                self.laps[-1].finish(event.last_lap)
            
            self.laps.append(LapTracker())
        
        if event.current_lap > 0 and self.laps:
            self.laps[-1].process_event(event)
            self._prev_event = event
    
    def _save_dump(self, db: Storage):
        race_id, race_folder = db.create_session(
            car_id=5,
            best_lap_time=self._best_lap
        )

        for i, lap in enumerate(self.laps):
            lap.dump(race_folder, i+1)
            db.save_lap(i+1, race_id, lap.lap_time())

    def finish(self, db: Storage, event: TelemetryStat):
        print(event)
        print(self.laps)
        print(self.race_type)
        if self.race_type == RaceType.TIME_TRIAL:
            self.laps.pop()
        else:
            self.laps[-1].finish(event.last_lap)
        self._best_lap = event.best_lap
        return self._save_dump(db)
    