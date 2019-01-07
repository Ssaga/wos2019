from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPen, QPolygonF
from PyQt5.QtWidgets import QToolTip
from client.battlefield_item import WosBattlefieldItem
from client.ship_info import ShipInfo
import cCommonGame


class WosBattleShipItem(WosBattlefieldItem):
    def __init__(self, field_info, ship_id=0, length=5, is_sunken=False):
        WosBattlefieldItem.__init__(self, field_info)

        self.ship_info = ShipInfo(ship_id, cCommonGame.Position(0, 0))
        self.ship_info.size = length
        self.ship_info.is_sunken = is_sunken
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

        self.brushes = dict()
        self.brushes[ShipInfo.Type.FRIENDLY] = QBrush(QColor(0, 200, 0, 255))
        self.brushes[ShipInfo.Type.HOSTILE] = QBrush(QColor(200, 0, 0, 255))
        self.brushes[ShipInfo.Type.CIVILIAN] = QBrush(QColor(200, 200, 200, 255))
        self.brushes[ShipInfo.Type.UNKNOWN] = QBrush(QColor(200, 200, 0, 255))
        self.brushes[ShipInfo.Type.SHADOW] = QBrush(QColor(0, 0, 0, 128))
        self.pen = QPen(QColor(0, 0, 0, 255))

    def boundingRect(self):
        return QRectF(self.start_pos, self.end_pos)

    def draw_cross(self, painter):
        painter.setPen(QPen(QColor(255, 0, 0, 255), 3))
        rect = self.boundingRect()
        painter.drawLine(rect.topLeft(), rect.bottomRight())
        painter.drawLine(rect.topRight(), rect.bottomLeft())

    def get_ship_info(self):
        return self.ship_info

    def hoverEnterEvent(self, event):
        # self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(0, 0, 0, 255), 2)
        self.show_tool_tip(event)
        self.update()

    def hoverLeaveEvent(self, event):
        # self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(0, 0, 0, 255))
        QToolTip.hideText()
        self.update()

    def hoverMoveEvent(self, event):
        self.show_tool_tip(event)

    def mouseReleaseEvent(self, event):
        if self.drag_delta is not None:
            self.drag_delta = None
            self.snap_to_grid(self.pos().x(), self.pos().y())

        if event.button() == Qt.RightButton and self.is_draggable:
            self.rotate_ship()

    def paint(self, painter, style, widget=None):
        painter.setBrush(self.brushes[self.ship_info.type])
        painter.setPen(self.pen)
        painter.drawPolygon(self.body)
        if self.ship_info.is_sunken:
            self.draw_cross(painter)

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

    def set_ship_type(self, t):
        self.ship_info.set_type(t)

    def show_tool_tip(self, event):
        tool_tip = ''
        if self.ship_info.type is ShipInfo.Type.FRIENDLY:
            tool_tip = "Id: %s" % self.ship_info.ship_id
        else:
            tool_tip = ''
            if self.ship_info.type is ShipInfo.Type.CIVILIAN:
                tool_tip = "Civilian ship"
            elif self.ship_info.type is ShipInfo.Type.HOSTILE:
                tool_tip = "Hostile ship"
            elif self.ship_info.type is ShipInfo.Type.UNKNOWN:
                tool_tip = "Unidentified ship"
        if self.ship_info.is_sunken:
            tool_tip += '(Destroyed)'
        QToolTip.showText(event.screenPos(), tool_tip)

    def snap_to_grid(self, pos_x, pos_y):
        p = self.map_position_to_grid(pos_x, pos_y)
        self.set_grid_position(p.x(), p.y())
