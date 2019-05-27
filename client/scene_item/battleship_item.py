from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPen, QPolygonF
from PyQt5.QtWidgets import QToolTip
from client.item_depth_manager import WosItemDepthManager
from client.scene_item.battlefield_item import WosBattlefieldItem
from client.ship_info import ShipInfo
from client.wos import ItemType
import cCommonGame


class WosBattleShipItem(WosBattlefieldItem):
    def __init__(self, field_info, drag_boundary, ship_id=0, length=5, is_sunken=False):
        WosBattlefieldItem.__init__(self, field_info)
        self.drag_boundary = drag_boundary

        self.ship_info = ShipInfo(ship_id, cCommonGame.Position(0, 0))
        self.ship_info.size = length
        self.ship_info.is_sunken = is_sunken
        self.ship_info.rotated.connect(self.ship_rotated)
        self.ship_info.moved.connect(self.ship_moved)

        self.set_type(ItemType.SHIP)
        WosItemDepthManager().set_depth(self)

        self.start_pos = QPointF()
        self.end_pos = QPointF()
        self.head = QPolygonF()
        self.tail = QPolygonF()
        self.body = QPolygonF()
        self.update_body()

        self.brushes = dict()
        self.brushes[ShipInfo.Type.FRIENDLY] = QBrush(QColor(0, 200, 0, 255))
        self.brushes[ShipInfo.Type.HOSTILE] = QBrush(QColor(200, 0, 0, 255))
        self.brushes[ShipInfo.Type.CIVILIAN] = QBrush(QColor(200, 200, 200, 255))
        self.brushes[ShipInfo.Type.UNKNOWN] = QBrush(QColor(200, 200, 0, 255))
        self.brushes[ShipInfo.Type.BLACK] = QBrush(QColor(255, 255, 255, 255))
        self.brushes[ShipInfo.Type.SHADOW] = QBrush(QColor(0, 0, 0, 0))
        self.pens = dict()
        self.pens[ShipInfo.Type.FRIENDLY] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.HOSTILE] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.CIVILIAN] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.UNKNOWN] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.BLACK] = QPen(QColor(0, 0, 0, 255))
        self.pens[ShipInfo.Type.SHADOW] = QPen(QColor(0, 255, 0, 255), 2, Qt.DashLine)
        self.pen = QPen(QColor(0, 0, 0, 255))

    def boundingRect(self):
        return QRectF(self.start_pos, self.end_pos)

    def clone(self):
        ship_item = WosBattleShipItem(self.field_info, self.ship_info.ship_id, self.ship_info.size,
                                      self.ship_info.is_sunken)
        ship_item.set_grid_position(self.ship_info.position.x, self.ship_info.position.y)
        ship_item.set_heading(self.ship_info.heading)
        ship_item.set_is_draggable(self.is_draggable)
        return ship_item

    def draw_cross(self, painter):
        painter.setPen(QPen(QColor(255, 0, 0, 255), 3))
        rect = self.boundingRect()
        painter.drawLine(rect.topLeft(), rect.bottomRight())
        painter.drawLine(rect.topRight(), rect.bottomLeft())

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

    def make_shadow(self, ship, actions):
        ship.set_grid_position(self.ship_info.position.x, self.ship_info.position.y)
        ship.set_heading(self.ship_info.heading)
        ship.set_size(self.ship_info.size)
        ship.set_ship_type(ShipInfo.Type.SHADOW)
        ship.set_type(ItemType.ANNOTATION)
        ship.set_is_hoverable(False)
        ship.set_is_sunken(self.ship_info.is_sunken)
        for action in actions:
            if action == cCommonGame.Action.FWD:
                ship.ship_info.move_forward()
            elif action == cCommonGame.Action.CW:
                ship.ship_info.turn_clockwise()
            elif action == cCommonGame.Action.CCW:
                ship.ship_info.turn_counter_clockwise()

    def mouseReleaseEvent(self, event):
        if self.drag_delta is not None:
            self.drag_delta = None
            self.snap_to_grid(self.pos().x(), self.pos().y())

        if event.button() == Qt.RightButton and self.is_draggable:
            self.rotate_ship()

    def paint(self, painter, style, widget=None):
        painter.setBrush(self.brushes[self.ship_info.type])
        painter.setPen(self.pens[self.ship_info.type])
        painter.drawPolygon(self.body)
        if self.ship_info.is_sunken:
            self.draw_cross(painter)

    def point_is_within(self, x, y):
        old_x = self.ship_info.position.x
        old_y = self.ship_info.position.y
        self.set_grid_position(x, y)
        positions = self.ship_info.get_placement()
        x1 = self.drag_boundary.min_x
        x2 = self.drag_boundary.max_x
        y1 = self.drag_boundary.min_y
        y2 = self.drag_boundary.max_y
        is_within = True
        for position in positions:
            if not (x1 <= position[0] < x2 and y1 <= position[1] < y2):
                is_within = False
                break
        self.set_grid_position(old_x, old_y)
        return is_within

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

    def set_is_sunken(self, is_sunken):
        self.ship_info.is_sunken = is_sunken

    def set_ship_type(self, t):
        self.ship_info.set_type(t)

    def set_size(self, length):
        self.ship_info.size = length
        self.update_body()

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
            elif self.ship_info.type is ShipInfo.Type.UNKNOWN or self.ship_info.type is ShipInfo.Type.BLACK:
                tool_tip = "Unidentified ship"
        if self.ship_info.is_sunken:
            tool_tip += ' - Destroyed'
        tool_tip += " (%s, %s)" % (self.ship_info.position.x, self.ship_info.position.y)
        QToolTip.showText(event.screenPos(), tool_tip)

    def snap_to_grid(self, pos_x, pos_y):
        p = self.map_position_to_grid(pos_x, pos_y)
        if self.drag_boundary is None or self.point_is_within(p.x(), p.y()):
            self.set_grid_position(p.x(), p.y())
        else:
            self.set_grid_position(self.ship_info.position.x, self.ship_info.position.y)

    def update_body(self):
        self.start_pos = QPointF(self.field_info.size.x() * 0.2, self.field_info.size.y() * 0.2)
        self.end_pos = QPointF(self.field_info.size.x() * 0.8,
                               self.ship_info.size * self.field_info.size.y() - self.start_pos.y())
        head_end_y = self.field_info.size.y() * 0.8

        # Center of origin at the middle of ship body (floor function)
        self.start_pos -= QPointF(0, self.field_info.size.y() * self.ship_info.get_y_center())
        self.end_pos -= QPointF(0, self.field_info.size.y() * self.ship_info.get_y_center())
        head_end_y -= self.field_info.size.y() * self.ship_info.get_y_center()

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
