from typing import Optional
from src.schema.telemetry import TelemetryStat
import os
from datetime import datetime
import pandas as pd
import time

from src.services.lap import LapTracker


class RaceTracker:
    def __init__(self):
        self.max_speed = -1
        self._start_time = time.time()
        self.cur_lap_idx = -1
        self.laps: list[LapTracker] = []

        self._prev_event: Optional[TelemetryStat] = None
    
    def _is_new_lap(self, event: TelemetryStat) -> bool:
        if self._prev_event is None:
            return True
        
        if event.current_lap > self._prev_event.current_lap:
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
        dirname = f"results/{save_time}"
        os.makedirs(dirname)

        for i in range(len(self.laps)):
            lap_label = f'lap_{i+1}'
            df = pd.DataFrame(
                [(
                    item.current_gear,
                    item.speed,
                    item.rpm,
                    item.throttle_rate,
                    item.brake_rate,
                    item.x,
                    item.y,
                ) for item in self.laps[i].stats],
                columns=['gear', 'speed', 'rpm', 'throttle', 'brake', 'x', 'y']
            )
            df.to_csv(f"{dirname}/{lap_label}.csv")
    
    def finish(self):
        self.laps[-1].finish()
        return self._save_dump()
    