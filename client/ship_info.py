from enum import Enum
import cCommonGame


class ShipInfo(cCommonGame.ShipInfo):
    class Type(Enum):
        FRIENDLY = 0
        HOSTILE = 1
        CIVILIAN = 2
        UNKNOWN = 3
        SHADOW = 4

    def __init__(self, ship_id=0, position=cCommonGame.Position(0, 0), heading=0, size=0, is_sunken=False, parent=None):
        cCommonGame.ShipInfo.__init__(self, ship_id, position, heading, size, is_sunken, parent)
        self.type = ShipInfo.Type.FRIENDLY

    def set_type(self, t):
        self.type = t
