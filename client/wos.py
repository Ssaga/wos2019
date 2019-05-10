from enum import Enum

# Client side common enums or classes, for common enums or classes used by both client and server see cCommongame.py

class ItemType(Enum):
    UNKNOWN = 0
    TERRAIN_LAND = 1
    TERRAIN_AIR = 2
    UW_SHIP = 3
    SHIP = 4
    ANNOTATION = 5
    BOUNDARY = 6
    TERRAIN_ON_HOVER = 999

class PlayerInfo:
    def __init__(self, player_id):
        self.player_id = player_id