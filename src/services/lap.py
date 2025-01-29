from src.schema.telemetry import TelemetryStat
import time


class LapTracker:
    def __init__(self):
        self._start_time = time.time()
        self.stats: list[TelemetryStat] = []
    
    def process_event(self, event: TelemetryStat):
        self.stats.append(event)
    
    def finish(self):
        lap_time = time.time() - self._start_time
        print(f"LAP END IN {lap_time}")
    