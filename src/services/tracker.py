from typing import Optional
from src.schema.telemetry import TelemetryStat

from src.services.race import RaceTracker


class Tracker:
    def __init__(self):
        self.is_race_running = False
        self.race_tracker: Optional[RaceTracker] = None
        self.prev_event: Optional[TelemetryStat] = None
    
    def _is_race_started(self, event: TelemetryStat) -> bool:
        if event.current_lap == 1 and not self.race_tracker and event.current_position > -1:
            return True
        
        return False
    
    def process_event(self, d_event: bytes):
        event = TelemetryStat.from_bytes(d_event)
        if event:
            if self.race_tracker:
                if event.current_lap > event.total_laps:
                    self.race_tracker.finish()
                    self.race_tracker = None
                    return
            else:
                if self._is_race_started(event):
                    self.race_tracker = RaceTracker()
            
            self.race_tracker.process_event(event)            
            self.prev_event = event

            return
    