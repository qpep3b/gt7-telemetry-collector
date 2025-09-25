from typing import Optional
from src.schema.telemetry import TelemetryStat

from src.services.lap import LapTracker
from src.storage import Storage


class RaceTracker:
    def __init__(self):
        self.max_speed = -1
        self.cur_lap_idx = -1
        self.laps: list[LapTracker] = []
        self.car_id: Optional[int] = None
        self.special_packet_time = 0.0

        self._prev_event: Optional[TelemetryStat] = None
        self._best_lap = None
    
    def _is_new_lap(self, event: TelemetryStat) -> bool:
        if event.current_lap <= 0:
            return False

        if event.current_lap > event.total_laps:
            return False

        if self._prev_event is None:
            return True
        
        if event.current_lap > self._prev_event.current_lap and event.current_lap <= event.total_laps:
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
        self.laps[-1].finish(event.last_lap)
        self._best_lap = event.best_lap
        return self._save_dump(db)
    