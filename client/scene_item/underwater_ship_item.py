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
    def __init__(self, field_info, ship_id=0, name='Underwater vehicle', x=0, y=0):
        WosBattlefieldItem.__init__(self, field_info)

        self.ship_info = UwShipInfo(ship_id, cCommonGame.Position(0, 0))

        self.set_type(ItemType.SHIP)
        self.ship_info.moved.connect(self.ship_moved)

        self.field_info = field_info
        self.name = name

        self.body = QRectF(5, 2, self.field_info.size.x() - 10, self.field_info.size.y() - 4)
        self.setRotation(30)

        self.brushes = dict()
        self.brushes[ShipInfo.Type.FRIENDLY] = QBrush(QColor(0, 200, 0, 255))
        self.brushes[ShipInfo.Type.HOSTILE] = QBrush(QColor(200, 0, 0, 255))
        self.brushes[ShipInfo.Type.CIVILIAN] = QBrush(QColor(200, 200, 200, 255))
        self.brushes[ShipInfo.Type.UNKNOWN] = QBrush(QColor(200, 200, 0, 255))
        self.brushes[ShipInfo.Type.SHADOW] = QBrush(QColor(0, 0, 0, 0))
        self.pens = dict()
        self.pens[ShipInfo.Type.FRIENDLY] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.HOSTILE] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.CIVILIAN] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.UNKNOWN] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.SHADOW] = QPen(QColor(0, 255, 0, 255), 2, Qt.DashLine)
        self.pen = QPen(QColor(0, 0, 0, 255))

    def boundingRect(self):
        return self.body

    def get_ship_info(self):
        return self.ship_info

    def hoverEnterEvent(self, event):
        self.pens[self.ship_info.type].setWidth(2)
        self.show_tool_tip(event)
        self.update()

    def hoverLeaveEvent(self, event):
        self.pens[self.ship_info.type].setWidth(1)
        QToolTip.hideText()
        self.update()

    def hoverMoveEvent(self, event):
        self.show_tool_tip(event)

    def paint(self, painter, style, widget=None):
        painter.setBrush(self.brushes[self.ship_info.type])
        painter.setPen(self.pens[self.ship_info.type])
        painter.drawEllipse(self.body)

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
        self.set_grid_position(p.x(), p.y())