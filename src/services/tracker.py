from typing import Optional
from src.schema.telemetry import TelemetryStat

from src.services.race import RaceTracker, RaceType
from src.storage import Storage


class Tracker:
    def __init__(self, db: Storage, debug=False):
        self.is_race_running = False
        self.race_tracker: Optional[RaceTracker] = None
        self.prev_event: Optional[TelemetryStat] = None
        self._db = db
        self._debug = debug

        self.all_events: list[TelemetryStat] = []
        self._current_race_type: Optional[RaceType] = None
    
    def _is_race_finished(self, event: TelemetryStat) -> bool:
        if not self.prev_event:
            return False

        if self._current_race_type == RaceType.RACE and event.current_lap > event.total_laps:
            return True

        if self._current_race_type == RaceType.TIME_TRIAL and event.in_race == False:
            return True

        if self._current_race_type == RaceType.REPLAY and event.current_lap > self.prev_event.current_lap and self.prev_event.current_lap > 0:
            return True
        
        return False
    
    def process_event(self, d_event: bytes):
        event = TelemetryStat.from_bytes(d_event, self.prev_event)
        self._process_parsed_event(event)
    
    def _get_race_type(self, event: TelemetryStat) -> Optional[RaceType]:
        if not event.in_race and event.current_position == 1 and event.total_racers == 1:
            return RaceType.REPLAY
        
        if event.in_race and event.total_laps == 0:
            return RaceType.TIME_TRIAL
        
        if event.total_laps:
            return RaceType.RACE

        # На случай, если похоже на начало круга, но на самом деле нет
        return None
    
    # for tests
    def _process_parsed_event(self, event: Optional[TelemetryStat]):
        if self._debug:
            self.all_events.append(event)
        if event:
            if self.race_tracker is None:
                ### Check start race
                if event.current_lap == 1 and (self.prev_event is None or self.prev_event.current_lap == 0):
                    ### RACE STARTED
                    self._current_race_type = self._get_race_type(event)
                    if self._current_race_type:
                        self.race_tracker = RaceTracker(self._current_race_type)

            if not self.race_tracker:
                self.prev_event = event
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
            
    