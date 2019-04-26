from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QToolTip
from client.scene_item.battlefield_item import WosBattlefieldItem
from client.wos import ItemType


class WosFireAnnotationItem(WosBattlefieldItem):
    def __init__(self, field_info, name, x, y):
        WosBattlefieldItem.__init__(self, field_info)
        self.field_info = field_info
        self.name = name
        self.x = 0
        self.y = 0
        self.body = QRectF()
        self.is_friendly = True
        self.set_position(x, y)

        self.set_is_draggable(False)
        self.set_is_hoverable(False)
        self.set_type(ItemType.ANNOTATION)

        self.pens = dict()
        self.pens[True] = QPen(QColor(0, 255, 0, 255), 2)
        self.pens[False] = QPen(QColor(255, 0, 0, 255), 2)

    def boundingRect(self):
        return self.body

    def hoverEnterEvent(self, event):
        self.pens[self.is_friendly].setWidth(3)
        # self.show_tool_tip(event)
        self.update()

    def hoverLeaveEvent(self, event):
        self.pens[self.is_friendly].setWidth(2)
        QToolTip.hideText()
        self.update()

    def hoverMoveEvent(self, event):
        self.show_tool_tip(event)

    def paint(self, painter, style, widget=None):
        painter.setPen(self.pens[self.is_friendly])
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
        self.update()

    def show_tool_tip(self, event):
        QToolTip.showText(event.screenPos(), "%s (%s, %s)" % (self.name, self.x, self.y))
