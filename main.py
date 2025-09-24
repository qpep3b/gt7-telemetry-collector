from src.receivers.gt7 import GT7Receiver
import sqlite3

from src.services.tracker import Tracker
import time

PS_IP = '192.168.1.27'
PS_PORT = 33740

# db = sqlite3.connect('.run/db.sqlite')
# cursor = db.cursor()
# cursor.execute("""

# """)

tracker = Tracker()

receiver = GT7Receiver(PS_IP, PS_PORT)
for event in receiver.stream_events():
    tracker.process_event(event)
