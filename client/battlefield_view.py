from PyQt5.QtCore import QLineF
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtWidgets import QGraphicsView
from client.terrain_item import WosTerrainItem
import cCommonGame


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

    def __init__(self, field_count=QPoint(120, 120), parent=None):
        QGraphicsView.__init__(self, parent)

        scene = QGraphicsScene(self)
        scene.setSceneRect(0, 0, 10000, 10000)
        self.setScene(scene)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.centerOn(0, 0)
        self.setBackgroundBrush(QBrush(QColor(0, 0, 200, 128)))

        self.field_info = WosFieldInfo(QPoint(40, 40), QPoint(20, 20), field_count)

        self.field_lines = []
        self.labels = []

        self.field_types = [cCommonGame.MapData.ISLAND, cCommonGame.MapData.CLOUD_FRIENDLY,
                            cCommonGame.MapData.CLOUD_HOSTILE, cCommonGame.MapData.ISLAND]

        self.brushes = dict()
        self.brushes[cCommonGame.MapData.WATER] = QBrush(QColor(0, 0, 0, 0))
        self.brushes[cCommonGame.MapData.ISLAND] = QBrush(QColor(194, 194, 64, 255), Qt.Dense1Pattern)
        self.brushes[cCommonGame.MapData.CLOUD_FRIENDLY] = QBrush(QColor(240, 240, 240, 128), Qt.Dense1Pattern)
        self.brushes[cCommonGame.MapData.CLOUD_HOSTILE] = QBrush(QColor(240, 240, 240, 255), Qt.Dense1Pattern)
        self.brushes[cCommonGame.MapData.FOG_OF_WAR] = QBrush(QColor(200, 200, 200, 255), Qt.Dense1Pattern)

        self.update_field()

    def get_field_info(self):
        return self.field_info

    def grid_to_pos(self, grid):
        return QPointF(self.field_info.top_left.x() + grid.x() * self.field_info.size.x(),
                       self.field_info.top_left.y() + grid.y() * self.field_info.size.y())

    def update_field(self, map_data=None):
        scene = self.scene()
        scene.clear()
        self.field_lines = []
        self.labels = []

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
            text_item.setPos(self.grid_to_pos(QPointF(i, -1)))
            if i < 100:
                text_item.setFont(font)
            else:
                text_item.setFont(smaller_font)
            scene.addItem(text_item)
        for i in range(0, self.field_info.dimension.y()):
            text_item = QGraphicsTextItem(str(i))
            text_item.setPos(self.grid_to_pos(QPointF(-1, i)))
            if i < 100:
                text_item.setFont(font)
            else:
                text_item.setFont(smaller_font)
            scene.addItem(text_item)

        dark_gray_pen = QPen(QColor(25, 25, 25))
        for i in self.field_lines:
            scene.addLine(i, dark_gray_pen)

        if map_data is not None:
            for col in range(0, len(map_data)):
                for row in range(0, len(map_data[0])):
                    val = int(map_data[col][row])
                    # item = WosTerrainItem(self.field_info, col, row, val)
                    # scene.addItem(item)

    def grid_to_pixel(self, x, y):
        return self.field_info.top_left.x() + x * self.field_info.size.x(), \
               self.field_info.top_left.y() + y * self.field_info.size.y()

    def update_map(self, map_data):
        self.field_info.set_dimension(QPoint(len(map_data), len(map_data[0])))
        self.update_field(map_data)

    def set_dimension(self, x, y):
        self.field_info.set_dimension(QPoint(x, y))
        self.update_field()

    def place_item(self, item, grid):
        item.setPos(self.grid_to_pos(grid))
