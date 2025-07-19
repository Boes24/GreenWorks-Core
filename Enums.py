from enum import Enum

class MowerState(Enum):
    Parked_by_user = 2
    PAUSED = 3
    MOWING = 4
    SEARCHING_FOR_CHARGING_STATION = 6
    CHARGING = 7