from enum import Enum
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from client.ship_info import ShipInfo
import cCommonGame


class UwShipInfo(cCommonGame.UwShipInfo, QObject):
    moved = pyqtSignal(int, int)

    def __init__(self, ship_id=0, position=cCommonGame.Position(0, 0), size=0, is_sunken=False, parent=None):
        cCommonGame.UwShipInfo.__init__(self, ship_id, position, size, is_sunken)
        QObject.__init__(self, parent)
        self.type = ShipInfo.Type.FRIENDLY

    def set_position(self, x, y):
        super().set_position(x, y)
        self.moved.emit(self.position.x, self.position.y)

    def set_type(self, t):
        self.type = t

