from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsItem


class WosBattlefieldItem(QGraphicsItem):
    def __init__(self, field_info, ship_id=0):
        QGraphicsItem.__init__(self)
        self.field_info = field_info

        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.setTransformOriginPoint(self.field_info.size.x() / 2, self.field_info.size.y() / 2)

        # Used as a boolean to determine whether item is being moved, also used as the delta between the control point
        # of the item and the mouse cursor
        self.drag_delta = None

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

    def snap_to_grid(self, pos_x, pos_y):
        pass