from PyQt5.QtCore import QRectF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QToolTip
from client.scene_item.battlefield_item import WosBattlefieldItem
from client.wos import ItemType
import cCommonGame


class WosTerrainItem(WosBattlefieldItem):
    def __init__(self, field_info, x, y, t):
        WosBattlefieldItem.__init__(self, field_info)
        self.x = x
        self.y = y
        self.terrain_type = cCommonGame.MapData.WATER

        self.set_terrain_type(t)
        self.set_is_draggable(False)

        self.terrains = {cCommonGame.MapData.WATER: 'Water',
                         cCommonGame.MapData.ISLAND: 'Island',
                         cCommonGame.MapData.CLOUD_FRIENDLY: 'Cloud',
                         cCommonGame.MapData.CLOUD_HOSTILE: 'Cloud',
                         cCommonGame.MapData.FOG_OF_WAR: 'Fog'}

        # Brushes for different terrain type, one terrain type may have multiple brushes
        self.brushes = dict()
        self.brushes[cCommonGame.MapData.WATER] = [QBrush(QColor(0, 0, 0, 0)), Qt.Dense7Pattern]
        self.brushes[cCommonGame.MapData.ISLAND] = [QBrush(QColor(194, 194, 64, 255), Qt.Dense1Pattern)]
        self.brushes[cCommonGame.MapData.CLOUD_FRIENDLY] = [QBrush(QColor(240, 240, 240, 128), Qt.Dense1Pattern)]
        self.brushes[cCommonGame.MapData.CLOUD_HOSTILE] = [QBrush(QColor(240, 240, 240, 255), Qt.SolidPattern),
                                                           QBrush(QColor(0, 0, 0, 255), Qt.FDiagPattern)]
        self.brushes[cCommonGame.MapData.FOG_OF_WAR] = [QBrush(QColor(100, 100, 100, 255), Qt.SolidPattern),
                                                        QBrush(QColor(0, 0, 0, 255), Qt.FDiagPattern)]
        self.pen = QPen(QColor(0, 0, 0, 255))

        pixel = self.map_grid_to_position(x, y)
        self.body = QRectF(pixel.x(), pixel.y(), field_info.size.x(), field_info.size.y())

    def boundingRect(self):
        return self.body

    def hoverEnterEvent(self, event):
        self.pen = QPen(QColor(0, 0, 0, 255), 2)
        self.show_tool_tip(event)
        self.update()

    def hoverLeaveEvent(self, event):
        self.pen = QPen(QColor(0, 0, 0, 255))
        QToolTip.hideText()
        self.update()

    def hoverMoveEvent(self, event):
        self.show_tool_tip(event)

    def paint(self, painter, style, widget=None):
        painter.setPen(self.pen)

        if self.terrain_type == cCommonGame.MapData.WATER:
            brushes = self.brushes[cCommonGame.MapData.WATER]
            for brush in brushes:
                painter.setBrush(brush)
                painter.drawRect(self.body)
        else:
            for terrain in self.terrains:
                if self.terrain_type & terrain:
                    brushes = self.brushes[terrain]
                    for brush in brushes:
                        painter.setBrush(brush)
                        painter.drawRect(self.body)

    def set_terrain_type(self, t):
        self.terrain_type = t
        if self.terrain_type == cCommonGame.MapData.WATER or self.terrain_type == cCommonGame.MapData.ISLAND:
            self.set_type(ItemType.TERRAIN_LAND)
        else:
            self.set_type(ItemType.TERRAIN_AIR)
        self.update()

    def show_tool_tip(self, event):
        terrains = list()
        for field, field_str in self.terrains.items():
            if self.terrain_type & field:
                terrains.append(field_str)

        if len(terrains) == 0:
            terrains.append(self.terrains[cCommonGame.MapData.WATER])

        if self.terrain_type == cCommonGame.MapData.FOG_OF_WAR:
            terrains = [self.terrains[cCommonGame.MapData.FOG_OF_WAR]]

        QToolTip.showText(event.screenPos(), "%s (%s, %s)" % (' & '.join(terrains), self.x, self.y))
