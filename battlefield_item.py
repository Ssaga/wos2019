from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsItem
import cCommonGame


class WosBattlefieldItem(QGraphicsItem):
    def __init__(self, field_info):
        QGraphicsItem.__init__(self)
        self.field_info = field_info

        self.ship_info = cCommonGame.ShipInfo()
        self.ship_info.rotated.connect(self.ship_rotated)
        self.ship_info.moved.connect(self.ship_moved)

        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.setTransformOriginPoint(self.field_info.size.x() / 2, self.field_info.size.y() / 2)

        # Used as a boolean to determine whether item is being moved, also used as the delta between the control point
        # of the item and the mouse cursor
        self.drag_delta = None

    def get_ship_info(self):
        return self.ship_info

    def map_grid_to_position(self, x, y):
        return QPoint(self.field_info.top_left.x() + x * self.field_info.size.x(),
                      self.field_info.top_left.y() + y * self.field_info.size.y())

    def map_position_to_grid(self, pos_x, pos_y):
        return QPoint(round((pos_x - self.field_info.top_left.x()) / self.field_info.size.x()),
                      round((pos_y - self.field_info.top_left.y()) / self.field_info.size.y()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # self.drag_delta = self.mapToItem(self, event.pos())
            self.drag_delta = self.field_info.size / 2

    def mouseMoveEvent(self, event):
        if self.drag_delta is not None:
            self.setPos(self.mapToParent(event.pos()) - self.drag_delta)

    def mouseReleaseEvent(self, event):
        if self.drag_delta is not None:
            self.drag_delta = None
            self.snap_to_grid(self.pos().x(), self.pos().y())

        if event.button() == Qt.RightButton:
            self.rotate_ship()

    def rotate_ship(self):
        self.ship_info.turn_clockwise()

    def set_grid_position(self, x, y):
        self.ship_info.set_position(x, y)

    def ship_rotated(self, heading):
        self.setRotation(heading)

    def ship_moved(self, x, y):
        self.setPos(self.map_grid_to_position(x, y))

    def snap_to_grid(self, pos_x, pos_y):
        p = self.map_position_to_grid(pos_x, pos_y)
        self.set_grid_position(p.x(), p.y())
