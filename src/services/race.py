from typing import Optional
from src.schema.telemetry import TelemetryStat
import os
from datetime import datetime

from src.services.lap import LapTracker


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
    
    def _save_dump(self):
        save_time = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
        # dirname = f"results/{save_time}"
        dirname = "tracks/catalunya/grand-prix"

        os.makedirs(dirname, exist_ok=True)

        for i, lap in enumerate(self.laps):
            lap.dump(dirname, i+1)
    
    def finish(self):
        self.laps[-1].finish()
        return self._save_dump()
    