from src.schema.telemetry import TelemetryStat
import pandas as pd


class LapTracker:
    def __init__(self):
        self.stats: list[TelemetryStat] = []
        # print("LAP START")
    
    def process_event(self, event: TelemetryStat):
        self.stats.append(event)
    
    def finish(self):
        """
        !!!TODO!!!
        # Adapted from https://www.gtplanet.net/forum/threads/gt7-is-compatible-with-motion-rig.410728/post-13810797
        self.current_lap.lap_live_time = (self.current_lap.lap_ticks * 1. / 60.) - (self.session.special_packet_time / 1000.)
        """
        lap_time = self.stats[-1].time_on_track - self.stats[0].time_on_track
        # print(f"LAP END IN {lap_time}")
    
    def lap_time(self):
        return self.stats[-1].time_on_track - self.stats[0].time_on_track
    
    def dump(self, dirname: str, idx: int):
        lap_label = f'lap_{idx}'
        df = pd.DataFrame(
            [(
                # item.current_gear,
                # item.speed,
                # item.rpm,
                # item.throttle_rate,
                # item.brake_rate,
                # item.time_on_track,
                item.x,
                item.y,
                item.z,
                # item.lap_distance,
            ) for item in self.stats],
            columns=[
                # 'gear',
                # 'speed',
                # 'rpm',
                # 'throttle',
                # 'brake',
                # 'time',
                'x',
                'y',
                'z',
                # 'dist',
            ]
        )
        df.to_csv(f"{dirname}/{lap_label}.csv")
    