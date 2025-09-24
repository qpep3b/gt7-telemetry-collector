from typing import Optional
from src.schema.telemetry import TelemetryStat

from src.services.race import RaceTracker
from src.storage import Storage


class Tracker:
    def __init__(self, db: Storage):
        self.is_race_running = False
        self.race_tracker: Optional[RaceTracker] = None
        self.prev_event: Optional[TelemetryStat] = None
        self._db = db
    
    def _is_race_started(self, event: TelemetryStat) -> bool:
        if self.race_tracker: return False

        if event.total_racers > 0 and event.current_position > 0 and (self.prev_event is None or self.prev_event.current_position < -1 and self.prev_event.current_lap <= 0) and event.current_lap > 0:
            return True
        
        return False
    
    def process_event(self, d_event: bytes):
        event = TelemetryStat.from_bytes(d_event, self.prev_event)
        if event:
            if self._is_race_started(event):
                print("started")
                self.race_tracker = RaceTracker()
            if not self.race_tracker:
                return
            

            if (event.total_racers == -1 and self.prev_event is not None and self.prev_event.total_racers > 0) or event.current_lap > event.total_laps:
                print("FINISH")
                self.race_tracker.finish(self._db)
                self.race_tracker = None
                self.prev_event = None
                return
            
            self.race_tracker.process_event(event)

            self.prev_event = event
            
    