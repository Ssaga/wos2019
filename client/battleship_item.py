from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPen, QPolygonF
from client.battlefield_item import WosBattlefieldItem
import cCommonGame


class WosBattleShipItem(WosBattlefieldItem):
    def __init__(self, field_info, ship_id=0, length=5):
        WosBattlefieldItem.__init__(self, field_info, ship_id)

        self.ship_info = cCommonGame.ShipInfo(ship_id, cCommonGame.Position(0, 0))
        self.ship_info.size = length
        self.ship_info.rotated.connect(self.ship_rotated)
        self.ship_info.moved.connect(self.ship_moved)

        self.start_pos = QPointF(field_info.size.x() * 0.2, field_info.size.y() * 0.2)
        self.end_pos = QPointF(field_info.size.x() * 0.8,
                               self.ship_info.size * field_info.size.y() - self.start_pos.y())

        head_end_y = field_info.size.y() * 0.8
        self.head = QPolygonF(
            [QPointF(self.start_pos.x(), head_end_y),
             QPointF((self.end_pos.x() + self.start_pos.x()) / 2, self.start_pos.y()),
             QPointF(self.end_pos.x(), head_end_y)])

        self.tail = QPolygonF(
            [QPointF(self.start_pos.x(), head_end_y),
             QPointF(self.start_pos.x(), self.end_pos.y()),
             QPointF(self.end_pos.x(), self.end_pos.y()),
             QPointF(self.end_pos.x(), head_end_y)])

        self.body = QPolygonF(self.head + self.tail)

        self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(200, 0, 0, 255))

    def boundingRect(self):
        return QRectF(self.start_pos, self.end_pos)

    def get_ship_info(self):
        return self.ship_info

    def hoverEnterEvent(self, event):
        self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(255, 255, 0, 255), 2)
        self.update()

    def hoverLeaveEvent(self, event):
        self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(200, 0, 0, 255))
        self.update()

    def mouseReleaseEvent(self, event):
        if self.drag_delta is not None:
            self.drag_delta = None
            self.snap_to_grid(self.pos().x(), self.pos().y())

        if event.button() == Qt.RightButton:
            self.rotate_ship()

    def paint(self, painter, style, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawPolygon(self.body)

    def rotate_ship(self):
        self.ship_info.turn_clockwise()

    def ship_rotated(self, heading):
        self.setRotation(heading)

    def ship_moved(self, x, y):
        self.setPos(self.map_grid_to_position(x, y))

    def set_grid_position(self, x, y):
        self.ship_info.set_position(x, y)

    def set_heading(self, heading):
        self.ship_info.set_heading(heading)

    def snap_to_grid(self, pos_x, pos_y):
        p = self.map_position_to_grid(pos_x, pos_y)
        self.set_grid_position(p.x(), p.y())
