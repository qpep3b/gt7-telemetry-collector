import struct

from pydantic import BaseModel

from src.utils.math import dist_between


# ruff: noqa: F841
class TelemetryStat(BaseModel):
    package_id: int
    current_lap: int

    current_gear: int
    suggested_gear: int

    speed: int
    total_laps: int

    current_position: int
    total_racers: int

    rpm: float

    throttle_rate: int
    brake_rate: int

    x: float
    y: float
    z: float

    time_on_track: float
    lap_distance: float

    best_lap: int
    last_lap: int

    in_race: bool
    car_id: int

    @classmethod
    def from_bytes(
        cls, ddata: bytes, prev_event: "TelemetryStat | None"
    ) -> "TelemetryStat | None":
        package_id = struct.unpack("i", ddata[0x70 : 0x70 + 4])[0]
        best_lap = struct.unpack("i", ddata[0x78 : 0x78 + 4])[0]
        last_lap = struct.unpack("i", ddata[0x7C : 0x7C + 4])[0]
        current_lap = struct.unpack("h", ddata[0x74 : 0x74 + 2])[0]

        # if current_lap <= 0:
        #     return None

        current_gear = struct.unpack("B", ddata[0x90 : 0x90 + 1])[0] & 0b00001111
        suggested_gear = struct.unpack("B", ddata[0x90 : 0x90 + 1])[0] >> 4
        fuel_capacity = struct.unpack("f", ddata[0x48 : 0x48 + 4])[0]
        current_fuel = struct.unpack("f", ddata[0x44 : 0x44 + 4])[0]  # fuel
        boost = struct.unpack("f", ddata[0x50 : 0x50 + 4])[0] - 1

        tyre_diameter_FL = struct.unpack("f", ddata[0xB4 : 0xB4 + 4])[0]
        tyre_diameter_FR = struct.unpack("f", ddata[0xB8 : 0xB8 + 4])[0]
        tyre_diameter_RL = struct.unpack("f", ddata[0xBC : 0xBC + 4])[0]
        tyre_diameter_RR = struct.unpack("f", ddata[0xC0 : 0xC0 + 4])[0]

        type_speed_FL = abs(
            3.6 * tyre_diameter_FL * struct.unpack("f", ddata[0xA4 : 0xA4 + 4])[0]
        )
        type_speed_FR = abs(
            3.6 * tyre_diameter_FR * struct.unpack("f", ddata[0xA8 : 0xA8 + 4])[0]
        )
        type_speed_RL = abs(
            3.6 * tyre_diameter_RL * struct.unpack("f", ddata[0xAC : 0xAC + 4])[0]
        )
        tyre_speed_RR = abs(
            3.6 * tyre_diameter_RR * struct.unpack("f", ddata[0xB0 : 0xB0 + 4])[0]
        )

        car_speed = 3.6 * struct.unpack("f", ddata[0x4C : 0x4C + 4])[0]

        if car_speed > 0:
            tyre_slip_ratio_FL = "{:6.2f}".format(type_speed_FL / car_speed)
            tyre_slip_ratio_FR = "{:6.2f}".format(type_speed_FR / car_speed)
            tyre_slip_ratio_RL = "{:6.2f}".format(type_speed_RL / car_speed)
            tyre_slip_ratio_RR = "{:6.2f}".format(tyre_speed_RR / car_speed)

        time_on_track = struct.unpack("i", ddata[0x80 : 0x80 + 4])[
            0
        ]  # time of day on track

        total_laps = struct.unpack("h", ddata[0x76 : 0x76 + 2])[0]  # total laps

        current_position = struct.unpack("h", ddata[0x84 : 0x84 + 2])[
            0
        ]  # current position
        total_positions = struct.unpack("h", ddata[0x86 : 0x86 + 2])[
            0
        ]  # total positions

        car_id = struct.unpack("i", ddata[0x124 : 0x124 + 4])[0]  # car id

        throttle = struct.unpack("B", ddata[0x91 : 0x91 + 1])[0] / 2.55  # throttle
        rpm = struct.unpack("f", ddata[0x3C : 0x3C + 4])[0]  # rpm
        rpm_rev_warning = struct.unpack("H", ddata[0x88 : 0x88 + 2])[
            0
        ]  # rpm rev warning

        brake = struct.unpack("B", ddata[0x92 : 0x92 + 1])[0] / 2.55  # brake

        boost = struct.unpack("f", ddata[0x50 : 0x50 + 4])[0] - 1  # boost

        rpm_rev_limiter = struct.unpack("H", ddata[0x8A : 0x8A + 2])[
            0
        ]  # rpm rev limiter

        estimated_top_speed = struct.unpack("h", ddata[0x8C : 0x8C + 2])[
            0
        ]  # estimated top speed

        clutch = struct.unpack("f", ddata[0xF4 : 0xF4 + 4])[0]  # clutch
        clutch_engaged = struct.unpack("f", ddata[0xF8 : 0xF8 + 4])[0]  # clutch engaged
        rpm_after_clutch = struct.unpack("f", ddata[0xFC : 0xFC + 4])[
            0
        ]  # rpm after clutch

        oil_temp = struct.unpack("f", ddata[0x5C : 0x5C + 4])[0]  # oil temp
        water_temp = struct.unpack("f", ddata[0x58 : 0x58 + 4])[0]  # water temp

        oil_pressure = struct.unpack("f", ddata[0x54 : 0x54 + 4])[0]  # oil pressure
        ride_height = (
            1000 * struct.unpack("f", ddata[0x38 : 0x38 + 4])[0]
        )  # ride height

        tyre_temp_FL = struct.unpack("f", ddata[0x60 : 0x60 + 4])[0]  # tyre temp FL
        tyre_temp_FR = struct.unpack("f", ddata[0x64 : 0x64 + 4])[0]  # tyre temp FR

        suspension_fl = struct.unpack("f", ddata[0xC4 : 0xC4 + 4])[0]  # suspension FL
        suspension_fr = struct.unpack("f", ddata[0xC8 : 0xC8 + 4])[0]  # suspension FR

        tyre_temp_rl = struct.unpack("f", ddata[0x68 : 0x68 + 4])[0]  # tyre temp RL
        tyre_temp_rr = struct.unpack("f", ddata[0x6C : 0x6C + 4])[0]  # tyre temp RR

        suspension_rl = struct.unpack("f", ddata[0xCC : 0xCC + 4])[0]  # suspension RL
        suspension_rr = struct.unpack("f", ddata[0xD0 : 0xD0 + 4])[0]  # suspension RR

        gear_1 = struct.unpack("f", ddata[0x104 : 0x104 + 4])[0]  # 1st gear
        gear_2 = struct.unpack("f", ddata[0x108 : 0x108 + 4])[0]  # 2nd gear
        gear_3 = struct.unpack("f", ddata[0x10C : 0x10C + 4])[0]  # 3rd gear
        gear_4 = struct.unpack("f", ddata[0x110 : 0x110 + 4])[0]  # 4th gear
        gear_5 = struct.unpack("f", ddata[0x114 : 0x114 + 4])[0]  # 5th gear
        gear_6 = struct.unpack("f", ddata[0x118 : 0x118 + 4])[0]  # 6th gear
        gear_7 = struct.unpack("f", ddata[0x11C : 0x11C + 4])[0]  # 7th gear
        gear_8 = struct.unpack("f", ddata[0x120 : 0x120 + 4])[0]  # 8th gear

        # struct.unpack('f', ddata[0x100:0x100+4])[0]					# ??? gear

        position_x = struct.unpack("f", ddata[0x04 : 0x04 + 4])[0]  # pos X
        position_y = struct.unpack("f", ddata[0x08 : 0x08 + 4])[0]  # pos Y
        position_z = -struct.unpack("f", ddata[0x0C : 0x0C + 4])[0]  # pos Z

        velocity_x = struct.unpack("f", ddata[0x10 : 0x10 + 4])[0]  # velocity X
        velocity_y = struct.unpack("f", ddata[0x14 : 0x14 + 4])[0]  # velocity Y
        velocity_z = struct.unpack("f", ddata[0x18 : 0x18 + 4])[0]  # velocity Z

        rotation_pitch = struct.unpack("f", ddata[0x1C : 0x1C + 4])[0]  # rot Pitch
        rotation_yaw = struct.unpack("f", ddata[0x20 : 0x20 + 4])[0]  # rot Yaw
        rotation_roll = struct.unpack("f", ddata[0x24 : 0x24 + 4])[0]  # rot Roll

        angular_velocity_x = struct.unpack("f", ddata[0x2C : 0x2C + 4])[
            0
        ]  # angular velocity X
        angular_velocity_y = struct.unpack("f", ddata[0x30 : 0x30 + 4])[
            0
        ]  # angular velocity Y
        angular_velocity_z = struct.unpack("f", ddata[0x34 : 0x34 + 4])[
            0
        ]  # angular velocity Z

        is_paused = bin(struct.unpack("B", ddata[0x8E : 0x8E + 1])[0])[-2] == "1"
        in_race = bin(struct.unpack("B", ddata[0x8E : 0x8E + 1])[0])[-1] == "1"

        lap_distance = (
            0
            if prev_event is None or current_lap != prev_event.current_lap
            else prev_event.lap_distance
            + dist_between(
                prev_event.x,
                prev_event.y,
                prev_event.z,
                position_x,
                position_z,
                position_y,
            )
        )

        return cls(
            package_id=package_id,
            current_lap=current_lap,
            total_laps=total_laps,
            current_gear=current_gear,
            suggested_gear=suggested_gear,
            speed=int(car_speed),
            rpm=rpm,
            current_position=current_position,
            total_racers=total_positions,
            throttle_rate=int(throttle),
            brake_rate=int(brake),
            x=position_x,
            y=position_z,
            z=position_y,
            time_on_track=time_on_track,
            lap_distance=lap_distance,
            best_lap=int(best_lap),
            last_lap=int(last_lap),
            in_race=in_race,
            car_id=int(car_id),
        )
