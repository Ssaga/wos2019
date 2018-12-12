from PyQt5.QtCore import QLineF, QMimeData, QPoint, QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QDrag, QPen, QPolygonF
from battlefield_item import WosBattlefieldItem


class WosBattleShipItem(WosBattlefieldItem):
    def __init__(self, field_info, length=5):
        WosBattlefieldItem.__init__(self, field_info)

        self.length = length
        self.start_pos = QPointF(field_info.size.x() * 0.2, field_info.size.y() * 0.2)
        self.end_pos = QPointF(field_info.size.x() * 0.8, self.length * field_info.size.y() - self.start_pos.y())

        head_end_y = field_info.size.y() * 0.8
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

        self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(200, 0, 0, 255))

    def boundingRect(self):
        return QRectF(self.start_pos, self.end_pos)

    def hoverEnterEvent(self, event):
        self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(255, 255, 0, 255), 2)
        self.update()

    def hoverLeaveEvent(self, event):
        self.brush = QBrush(QColor(200, 0, 0, 255))
        self.pen = QPen(QColor(200, 0, 0, 255))
        self.update()

    def paint(self, painter, style, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawPolygon(self.body)
