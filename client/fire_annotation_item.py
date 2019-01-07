from PyQt5.QtCore import QRectF
from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QToolTip
from client.battlefield_item import WosBattlefieldItem
import cCommonGame


class WosFireAnnotationItem(WosBattlefieldItem):
    def __init__(self, field_info, name, x, y):
        WosBattlefieldItem.__init__(self, field_info)
        self.field_info = field_info
        self.name = name
        self.x = 0
        self.y = 0
        self.body = QRectF()
        self.set_position(x, y)

        self.set_is_draggable(False)
        self.set_is_hoverable(False)

        # todo: Consider depth manager class
        self.setZValue(2)

        self.brush = QBrush(QColor(255, 0, 0, 255))
        self.pen = QPen(QColor(255, 0, 0, 255), 2)

    def boundingRect(self):
        return self.body

    def hoverEnterEvent(self, event):
        # self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(255, 0, 0, 255), 3)
        # self.show_tool_tip(event)
        self.update()

    def hoverLeaveEvent(self, event):
        # self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(255, 0, 0, 255), 2)
        QToolTip.hideText()
        self.update()

    def hoverMoveEvent(self, event):
        self.show_tool_tip(event)

    def paint(self, painter, style, widget=None):
        painter.setPen(self.pen)
        rect = self.body
        painter.drawEllipse(rect)
        painter.drawLine(rect.topLeft(), rect.bottomRight())
        painter.drawLine(rect.topRight(), rect.bottomLeft())

    def set_x(self, x):
        self.set_position(int(x), self.y)

    def set_y(self, y):
        self.set_position(self.x, int(y))

    def set_position(self, x, y):
        self.x = x
        self.y = y
        pixel = self.map_grid_to_position(x, y)
        self.prepareGeometryChange()
        self.body = QRectF(pixel.x(), pixel.y(), self.field_info.size.x(), self.field_info.size.y())

    def show_tool_tip(self, event):
        QToolTip.showText(event.screenPos(), "%s (%s, %s)" % (self.name, self.x, self.y))
