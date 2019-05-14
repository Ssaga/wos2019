from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QToolTip
from client.scene_item.battlefield_item import WosBattlefieldItem
from client.ship_info import ShipInfo
from client.underwater.uw_ship_info import UwShipInfo
from client.wos import ItemType
import cCommonGame


class WosUnderwaterShipItem(WosBattlefieldItem):
    def __init__(self, field_info, drag_boundary, ship_id=0, name='Underwater vehicle', x=0, y=0):
        WosBattlefieldItem.__init__(self, field_info)
        self.drag_boundary = drag_boundary

        self.ship_info = UwShipInfo(ship_id, cCommonGame.Position(0, 0))

        self.set_type(ItemType.UW_SHIP)
        self.ship_info.moved.connect(self.ship_moved)

        self.field_info = field_info
        self.name = name

        self.body = QRectF(5, 2, self.field_info.size.x() - 10, self.field_info.size.y() - 4)
        self.setRotation(30)

        self.brushes = dict()
        self.brushes[ShipInfo.Type.FRIENDLY] = QBrush(QColor(0, 200, 0, 168))
        self.brushes[ShipInfo.Type.HOSTILE] = QBrush(QColor(200, 0, 0, 168))
        self.brushes[ShipInfo.Type.CIVILIAN] = QBrush(QColor(200, 200, 200, 168))
        self.brushes[ShipInfo.Type.UNKNOWN] = QBrush(QColor(200, 200, 0, 168))
        self.brushes[ShipInfo.Type.SHADOW] = QBrush(QColor(0, 0, 0, 0))
        self.brushes_hover = dict()
        self.brushes_hover[ShipInfo.Type.FRIENDLY] = QBrush(QColor(0, 200, 0, 255))
        self.brushes_hover[ShipInfo.Type.HOSTILE] = QBrush(QColor(200, 0, 0, 255))
        self.brushes_hover[ShipInfo.Type.CIVILIAN] = QBrush(QColor(200, 200, 200, 255))
        self.brushes_hover[ShipInfo.Type.UNKNOWN] = QBrush(QColor(200, 200, 0, 255))
        self.brushes_hover[ShipInfo.Type.SHADOW] = QBrush(QColor(0, 0, 0, 0))
        self.brush = self.brushes[self.ship_info.type]
        self.pens = dict()
        self.pens[ShipInfo.Type.FRIENDLY] = QPen(QColor(0, 0, 0, 168))
        self.pens[ShipInfo.Type.HOSTILE] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.CIVILIAN] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.UNKNOWN] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.SHADOW] = QPen(QColor(0, 255, 0, 255), 2, Qt.DashLine)
        self.pen = self.pens[self.ship_info.type]

    def boundingRect(self):
        return self.body

    def clone(self):
        ship_item = WosUnderwaterShipItem(self.field_info, self.ship_info.ship_id)
        ship_item.set_grid_position(self.ship_info.position.x, self.ship_info.position.y)
        ship_item.set_is_draggable(self.is_draggable)
        return ship_item

    def get_ship_info(self):
        return self.ship_info

    def hoverEnterEvent(self, event):
        self.brush = self.brushes_hover[self.ship_info.type]
        self.pens[self.ship_info.type].setWidth(2)
        self.show_tool_tip(event)
        self.update()

    def hoverLeaveEvent(self, event):
        self.brush = self.brushes[self.ship_info.type]
        self.pens[self.ship_info.type].setWidth(1)
        QToolTip.hideText()
        self.update()

    def hoverMoveEvent(self, event):
        self.show_tool_tip(event)

    def paint(self, painter, style, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pens[self.ship_info.type])
        painter.drawEllipse(self.body)

    def point_is_within(self, x, y):
        x1 = self.drag_boundary.min_x
        x2 = self.drag_boundary.max_x
        y1 = self.drag_boundary.min_y
        y2 = self.drag_boundary.max_y
        return x1 <= x < x2 and y1 <= y < y2

    def mouseReleaseEvent(self, event):
        if self.drag_delta is not None:
            self.drag_delta = None
            self.snap_to_grid(self.pos().x(), self.pos().y())

    def rotate_ship(self):
        pass

    def set_grid_position(self, x, y):
        self.ship_info.set_position(x, y)

    def set_is_sunken(self, is_sunken):
        self.ship_info.is_sunken = is_sunken

    def set_ship_type(self, t):
        self.ship_info.set_type(t)

    def ship_moved(self, x, y):
        self.setPos(self.map_grid_to_position(x, y))

    def show_tool_tip(self, event):
        QToolTip.showText(event.screenPos(),
                          "%s (%s, %s)" % (self.name, self.ship_info.position.x, self.ship_info.position.y))

    def snap_to_grid(self, pos_x, pos_y):
        p = self.map_position_to_grid(pos_x, pos_y)
        if self.drag_boundary is None or self.point_is_within(p.x(), p.y()):
            self.set_grid_position(p.x(), p.y())
        else:
            self.set_grid_position(self.ship_info.position.x, self.ship_info.position.y)
