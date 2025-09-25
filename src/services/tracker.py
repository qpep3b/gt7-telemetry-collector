from typing import Optional
from src.schema.telemetry import TelemetryStat

from src.services.race import RaceTracker
from src.storage import Storage


class Tracker:
    def __init__(self, db: Storage, debug=False):
        self.is_race_running = False
        self.race_tracker: Optional[RaceTracker] = None
        self.prev_event: Optional[TelemetryStat] = None
        self._db = db
        self._debug = debug

        self.all_events: list[TelemetryStat] = []
    
    def _is_race_started(self, event: TelemetryStat) -> bool:
        if self.race_tracker: return False

        if (self.prev_event is None or not self.prev_event.in_race) and event.in_race:
            return True
        
        return False
    
    def _is_race_finished(self, event: TelemetryStat) -> bool:
        if not self.race_tracker: return False

        if (self.prev_event is not None and self.prev_event.in_race) and not event.in_race:
            return True
        
        return False

    
    def process_event(self, d_event: bytes):
        event = TelemetryStat.from_bytes(d_event, self.prev_event)
        self._process_parsed_event(event)
    
    # for tests
    def _process_parsed_event(self, event: Optional[TelemetryStat]):
        if self._debug:
            self.all_events.append(event)
        if event:
            if self._is_race_started(event):
                print("Racing session started")
                self.race_tracker = RaceTracker()
            if not self.race_tracker:
                return
            

            if self._is_race_finished(event):
                self.race_tracker.finish(self._db, event)
                self.race_tracker = None
                self.prev_event = None

                if self._debug:
                    with open('dump.gtdata', 'w') as f:
                        f.writelines([f"{x.model_dump_json()}\n" for x in self.all_events])
                    self.all_events = []
                return
            
            self.race_tracker.process_event(event)

            self.prev_event = event
            
    