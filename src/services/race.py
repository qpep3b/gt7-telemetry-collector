from typing import Optional
from src.schema.telemetry import TelemetryStat

from src.services.lap import LapTracker
from src.storage import Storage


class RaceTracker:
    def __init__(self):
        self.max_speed = -1
        self.cur_lap_idx = -1
        self.laps: list[LapTracker] = []

        self._prev_event: Optional[TelemetryStat] = None
    
    def _is_new_lap(self, event: TelemetryStat) -> bool:
        if event.current_lap > event.total_laps:
            return False

        if self._prev_event is None:
            return True
        
        if event.current_lap > self._prev_event.current_lap and event.current_lap <= event.total_laps:
            return True
        
        return False

    def process_event(self, event: TelemetryStat):
        if self._is_new_lap(event):
            if len(self.laps):
                self.laps[-1].finish()
            
            self.laps.append(LapTracker())
        
        self.laps[-1].process_event(event)
        
        self._prev_event = event
    
    def _save_dump(self, db: Storage):
        best_lap_time = min([x.lap_time() for x in self.laps])
        race_id = db.create_session(
            car_id=5,
            best_lap_time=best_lap_time
        )
        dirname = f".run/storage/_data/{race_id}"

        for i, lap in enumerate(self.laps):
            lap.dump(dirname, i+1)
            db.save_lap(i+1, race_id, lap.lap_time())
    
    def finish(self, db: Storage):
        self.laps[-1].finish()
        return self._save_dump(db)
    