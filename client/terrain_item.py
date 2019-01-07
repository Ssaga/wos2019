from PyQt5.QtCore import QRectF
from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QToolTip
from client.battlefield_item import WosBattlefieldItem
import cCommonGame


class WosTerrainItem(WosBattlefieldItem):
    def __init__(self, field_info, x, y, t):
        WosBattlefieldItem.__init__(self, field_info)
        self.x = x
        self.y = y
        self.type = t

        self.set_is_draggable(False)

        self.field_types = {cCommonGame.MapData.WATER: 'Water', cCommonGame.MapData.ISLAND: 'Island',
                            cCommonGame.MapData.CLOUD_FRIENDLY: 'Cloud', cCommonGame.MapData.CLOUD_HOSTILE: 'Cloud',
                            cCommonGame.MapData.FOG_OF_WAR: 'Fog'}

        self.brushes = dict()
        self.brushes[cCommonGame.MapData.WATER] = QBrush(QColor(0, 0, 0, 0))
        self.brushes[cCommonGame.MapData.ISLAND] = QBrush(QColor(194, 194, 64, 255), Qt.Dense1Pattern)
        self.brushes[cCommonGame.MapData.CLOUD_FRIENDLY] = QBrush(QColor(240, 240, 240, 128), Qt.Dense1Pattern)
        self.brushes[cCommonGame.MapData.CLOUD_HOSTILE] = QBrush(QColor(240, 240, 240, 255), Qt.Dense1Pattern)
        self.brushes[cCommonGame.MapData.FOG_OF_WAR] = QBrush(QColor(100, 100, 100, 255), Qt.Dense1Pattern)

        self.pen = QPen(QColor(0, 0, 0, 255))

        pixel = self.map_grid_to_position(x, y)
        self.body = QRectF(pixel.x(), pixel.y(), field_info.size.x(), field_info.size.y())
        # todo: Consider depth manager class
        if self.type != cCommonGame.MapData.WATER:
            self.setZValue(1)

    def boundingRect(self):
        return self.body

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

    def paint(self, painter, style, widget=None):
        painter.setPen(self.pen)

        if self.type == cCommonGame.MapData.WATER:
            painter.setBrush(self.brushes[cCommonGame.MapData.WATER])
            painter.drawRect(self.body)
        else:
            for field in self.field_types:
                if self.type & field:
                    painter.setBrush(self.brushes[field])
                    painter.drawRect(self.body)

    def set_type(self, t):
        self.type = t
        if self.type is not cCommonGame.MapData.WATER:
            self.setZValue(1)
        self.update()

    def show_tool_tip(self, event):
        terrains = list()
        for field, field_str in self.field_types.items():
            if self.type & field:
                terrains.append(field_str)

        if len(terrains) == 0:
            terrains.append(self.field_types[cCommonGame.MapData.WATER])

        if self.type == cCommonGame.MapData.FOG_OF_WAR:
            terrains = [self.field_types[cCommonGame.MapData.FOG_OF_WAR]]

        QToolTip.showText(event.screenPos(), "%s (%s, %s)" % (' & '.join(terrains), self.x, self.y))
