from src.receivers.gt7 import GT7Receiver
from src.services.tracker import Tracker
from src.storage import Storage

PS_IP = "192.168.1.27"
PS_PORT = 33740

tracker = Tracker(
    db=Storage(verbose=True),
)

receiver = GT7Receiver(PS_IP, PS_PORT)
for event in receiver.stream_events():
    tracker.process_event(event)
