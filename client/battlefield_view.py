from PyQt5.QtCore import QLineF
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView


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
        self.centerOn(0, 0)
        self.setBackgroundBrush(QBrush(QColor(0, 0, 200, 128)))

        self.field_info = WosFieldInfo(QPoint(40, 40), QPoint(20, 20), field_count)

        self.field_lines = []

        self.island_brush = QBrush(QColor(194, 194, 64, 255), Qt.Dense1Pattern)
        self.friendly_cloud_brush = QBrush(QColor(240, 240, 240, 128), Qt.Dense1Pattern)
        self.hostile_cloud_brush = QBrush(QColor(240, 240, 240, 255), Qt.Dense1Pattern)

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

        dark_gray_pen = QPen(QColor(25, 25, 25))
        for i in self.field_lines:
            scene.addLine(i, dark_gray_pen)

        # todo: Use enum instead of magic number
        # todo: More graceful checks
        if map_data is not None:
            for col in range(0, len(map_data)):
                for row in range(0, len(map_data[0])):
                    val = int(map_data[col][row])
                    while val > 0:
                        brush = self.island_brush
                        if val & 1:
                            brush = self.island_brush
                            val -= 1
                        elif val & 2:
                            brush = self.friendly_cloud_brush
                            val -= 2
                        elif val & 4:
                            brush = self.hostile_cloud_brush
                            val -= 4
                        px, py = self.grid_to_pixel(col, row)
                        item = scene.addRect(px, py, self.field_info.size.x(), self.field_info.size.y(), dark_gray_pen,
                                             brush)
                        item.setZValue(1)

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