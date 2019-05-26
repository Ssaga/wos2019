from enum import Enum
import cCommonGame
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal


class ShipInfo(cCommonGame.ShipInfo, QObject):
    moved = pyqtSignal(int, int)
    rotated = pyqtSignal(float)

    class Type(Enum):
        FRIENDLY = 0
        HOSTILE = 1
        CIVILIAN = 2
        UNKNOWN = 3
        BLACK = 4
        SHADOW = 5

    def __init__(self, ship_id=0, position=cCommonGame.Position(0, 0), heading=0, size=0, is_sunken=False, parent=None):
        cCommonGame.ShipInfo.__init__(self, ship_id, position, heading, size, is_sunken)
        QObject.__init__(self, parent)
        self.type = ShipInfo.Type.FRIENDLY
        self.y_center = size / 2
        if size % 2 == 0:
            self.y_center -= 1

    def get_y_center(self):
        y_center = int(self.size / 2)
        if self.size % 2 == 0:
            y_center -= 1

        return y_center

    def set_type(self, t):
        self.type = t

    def move_forward(self):
        super().move_forward()
        self.moved.emit(self.position.x, self.position.y)

    def set_heading(self, heading):
        super().set_heading(heading)
        self.rotated.emit(self.heading)

    def set_position(self, x, y):
        super().set_position(x, y)
        self.moved.emit(self.position.x, self.position.y)

    def turn_clockwise(self):
        super().turn_clockwise()
        self.rotated.emit(self.heading)

    def turn_counter_clockwise(self):
        super().turn_counter_clockwise()
        self.rotated.emit(self.heading)
