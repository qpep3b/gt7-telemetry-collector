from src.domain.models import Lap
from src.schema.telemetry import TelemetryStat
from src.services.tracker import Tracker
from src.storage import Storage


class FakeEventStreamer:
    def __init__(self):
        self.data = []
        with open('./tests/dump.gtdata', 'r') as f:
            for line in f:
                self.data.append(TelemetryStat.parse_raw(line.strip()))
    
    def stream_events(self):
        for item in self.data:
            yield item


def test_lap_times():
    db = Storage('.test')
    tracker = Tracker(db=db)

    receiver = FakeEventStreamer()
    for event in receiver.stream_events():
        tracker._process_parsed_event(event)

    laps = db.get_all_laps()
    assert len(laps) == 3
    assert laps[0].time == 57730
    assert laps[1].time == 58603
    assert laps[2].time == 63024

    assert True