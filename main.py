import socket
from typing import Optional
from salsa20 import Salsa20_xor
from src.receivers.gt7 import GT7Receiver

from src.services.tracker import Tracker

PS_IP = '192.168.1.27'
PS_PORT = 33740

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', PS_PORT))
s.settimeout(2)
print('CONNECTED')

def send_hb(s: socket.socket):
    send_data = 'A'
    s.sendto(send_data.encode('utf-8'), (PS_IP, 33739))


def salsa20_dec(dat: bytes) -> Optional[bytes]:
    KEY = b'Simulator Interface Packet GT7 ver 0.0'
    # Seed IV is always located here
    oiv = dat[0x40:0x44]
    iv1 = int.from_bytes(oiv, byteorder='little')
    # Notice DEADBEAF, not DEADBEEF
    iv2 = iv1 ^ 0xDEADBEAF
    IV = bytearray()
    IV.extend(iv2.to_bytes(4, 'little'))
    IV.extend(iv1.to_bytes(4, 'little'))
    ddata = Salsa20_xor(dat, bytes(IV), KEY[0:32])
    magic = int.from_bytes(ddata[0:4], byteorder='little')
    if magic != 0x47375330:
        return None

    return ddata


tracker = Tracker()
pkg_cnt = 0
while True:
    try:
        data, _ = s.recvfrom(4096)
        rec = salsa20_dec(data)

        if not rec:
            continue

        tracker.process_event(rec)
    except Exception as e:
        send_hb(s)


# receiver = GT7Receiver(PS_IP, PS_PORT)
# for event in receiver.stream_events():
#     tracker.process_event(event)
