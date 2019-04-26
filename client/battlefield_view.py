from functools import reduce
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QLineF
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtWidgets import QGraphicsView
from client.item_depth_manager import WosItemDepthManager
from client.wos import ItemType
from client.scene_item.battleship_item import WosBattleShipItem
from client.scene_item.terrain_item import WosTerrainItem
from client.ship_info import ShipInfo
import cCommonGame
import operator


class WosFieldInfo:
    def __init__(self, pos=QPoint(40, 40), size=QPoint(20, 20), dimension=QPoint(120, 120)):
        self.top_left = pos
        self.size = size
        self.dimension = None
        self.bottom_right = None
        self.set_dimension(dimension)

    def set_dimension(self, dimension):
        self.dimension = dimension
        self.bottom_right = QPoint(self.top_left.x() + self.size.x() * self.dimension.x(),
                                   self.top_left.y() + self.size.y() * self.dimension.y())


class WosBattleFieldView(QGraphicsView):
    show_terrain_context_menu = pyqtSignal(QContextMenuEvent, int, int, int)
    show_battleship_context_menu = pyqtSignal(QContextMenuEvent, ShipInfo, int, int)

    def __init__(self, field_count=QPoint(120, 120), parent=None):
        QGraphicsView.__init__(self, parent)

        scene = QGraphicsScene(self)
        scene.setSceneRect(0, 0, 10000, 10000)
        self.setScene(scene)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.centerOn(0, 0)
        self.setBackgroundBrush(QBrush(QColor(0, 0, 200, 128)))

        self.field_info = WosFieldInfo(QPoint(40, 40), QPoint(20, 20), field_count)

        self.field_lines = list()
        self.field_lines_items = list()
        self.labels = list()
        self.labels_items = list()
        self.boundaries = dict()
        self.boundary_items = dict()
        self.terrain_items = list()

        self.field_types = [cCommonGame.MapData.ISLAND, cCommonGame.MapData.CLOUD_FRIENDLY,
                            cCommonGame.MapData.CLOUD_HOSTILE, cCommonGame.MapData.ISLAND]

        self.update_field()

    def clear(self):
        self.field_lines = list()
        self.field_lines_items = list()
        self.labels = list()
        self.labels_items = list()
        self.terrain_items = list()
        self.boundary_items = list()
        self.scene().clear()

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        scene_pos = self.mapToScene(event.pos())
        if isinstance(item, WosTerrainItem):
            self.show_terrain_context_menu.emit(event, item.terrain_type, item.x, item.y)
        elif isinstance(item, WosBattleShipItem):
            x, y = self.pixel_to_grid(scene_pos.x(), scene_pos.y())
            self.show_battleship_context_menu.emit(event, item.ship_info, x, y)

    def get_field_info(self):
        return self.field_info

    def grid_to_pos(self, grid):
        return QPointF(self.field_info.top_left.x() + grid.x() * self.field_info.size.x(),
                       self.field_info.top_left.y() + grid.y() * self.field_info.size.y())

    def update_field(self, map_data=None):
        scene = self.scene()
        for field_line in self.field_lines_items:
            scene.removeItem(field_line)
        for label in self.labels_items:
            scene.removeItem(label)
        if len(self.terrain_items) > 0:
            # Flatten 2d to 1d for traversing
            terrains = reduce(operator.concat, self.terrain_items)
            for terrain in terrains:
                scene.removeItem(terrain)
        for boundary in self.boundary_items:
            scene.removeItem(boundary)

        self.field_lines = list()
        self.field_lines_items = list()
        self.labels = list()
        self.labels_items = list()
        self.terrain_items = list()
        self.boundary_items = list()

        scene.setSceneRect(0,
                           0,
                           (self.field_info.dimension.x() + 1) * self.field_info.size.x() + \
                           self.field_info.top_left.x() + self.field_info.top_left.x(),
                           (self.field_info.dimension.y() + 1) * self.field_info.size.y() + \
                           self.field_info.top_left.y() + self.field_info.top_left.y())

        # Draw grids
        for i in range(0, self.field_info.dimension.x() + 1):
            self.field_lines.append(QLineF(self.field_info.top_left.x() + i * self.field_info.size.y(),
                                           self.field_info.top_left.y(),
                                           self.field_info.top_left.x() + i * self.field_info.size.y(),
                                           self.field_info.bottom_right.y()))
        for i in range(0, self.field_info.dimension.y() + 1):
            self.field_lines.append(QLineF(self.field_info.top_left.x(),
                                           self.field_info.top_left.y() + i * self.field_info.size.y(),
                                           self.field_info.bottom_right.x(),
                                           self.field_info.top_left.y() + i * self.field_info.size.y()))

        # Draw labels
        font = QFont('Calibri', self.field_info.size.x() / 2)
        smaller_font = QFont('Calibri', self.field_info.size.x() / 2.5)
        for i in range(0, self.field_info.dimension.x()):
            text_item = QGraphicsTextItem(str(i))
            pos = self.grid_to_pos(QPointF(i, -1))
            pos += QPointF(0, -self.field_info.size.y() / 4)
            text_item.setPos(pos)
            if i < 100:
                text_item.setFont(font)
            else:
                text_item.setFont(smaller_font)
            scene.addItem(text_item)
            self.labels_items.append(text_item)
        for i in range(0, self.field_info.dimension.y()):
            text_item = QGraphicsTextItem(str(i))
            text_item.setFont(font)
            pos = self.grid_to_pos(QPointF(-1, i))
            if i >= 10:
                pos += QPointF(-self.field_info.size.x() / 3, 0)
            if i >= 100:
                pos += QPointF(-self.field_info.size.x() / 3, 0)
            text_item.setPos(pos)
            scene.addItem(text_item)
            self.labels_items.append(text_item)

        # Draw grids
        pen = QPen(QColor(25, 25, 25))
        for i in self.field_lines:
            self.field_lines_items.append(scene.addLine(i, pen))

        # Draw grid data like water, island or clouds
        if map_data is not None:
            for col in range(0, len(map_data)):
                self.terrain_items.append(list())
                for row in range(0, len(map_data[0])):
                    val = int(map_data[col][row])
                    item = WosTerrainItem(self.field_info, col, row, val)
                    self.terrain_items[0].append(item)
                    scene.addItem(item)
        else:
            for col in range(0, self.field_info.dimension.x()):
                self.terrain_items.append(list())
                for row in range(0, self.field_info.dimension.y()):
                    item = WosTerrainItem(self.field_info, col, row, cCommonGame.MapData.WATER)
                    self.terrain_items[0].append(item)
                    scene.addItem(item)

        # Draw boundaries
        pen = QPen(QColor(0, 0, 0), 2)
        for boundary in self.boundaries.values():
            scene.addLine(QLineF(boundary.topLeft(), boundary.topRight()), pen)
            scene.addLine(QLineF(boundary.topRight(), boundary.bottomRight()), pen)
            scene.addLine(QLineF(boundary.bottomRight(), boundary.bottomLeft()), pen)
            scene.addLine(QLineF(boundary.bottomLeft(), boundary.topLeft()), pen)
        boundary_z = WosItemDepthManager().get_depths_by_item(ItemType.BOUNDARY)
        for boundary in self.boundary_items:
            boundary.setZValue(boundary_z)

    def grid_to_pixel(self, x, y):
        return self.field_info.top_left.x() + x * self.field_info.size.x(), \
               self.field_info.top_left.y() + y * self.field_info.size.y()

    def pixel_to_grid(self, x, y):
        return int((x - self.field_info.top_left.x()) / self.field_info.size.x()), \
               int((y - self.field_info.top_left.y()) / self.field_info.size.y())

    def update_boundaries(self, boundaries):
        if boundaries is None:
            return

        self.boundaries.clear()

        for player_id, boundary in boundaries.items():
            x1, y1 = self.grid_to_pixel(boundary.min_x, boundary.min_y)
            x2, y2 = self.grid_to_pixel(boundary.max_x, boundary.max_y)
            rect = QRectF(QPointF(x1, y1), QPointF(x2, y2))
            self.boundaries[player_id] = rect

    def update_map(self, map_data):
        self.field_info.set_dimension(QPoint(len(map_data), len(map_data[0])))
        self.update_field(map_data)

    def set_dimension(self, x, y):
        self.field_info.set_dimension(QPoint(x, y))
        self.update_field()

    def place_item(self, item, grid):
        item.setPos(self.grid_to_pos(grid))
