from PyQt5.Qt import QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont

class WosBoundaryLabelItem(QGraphicsTextItem):
    def __init__(self, player_id, boundary, parent=None):
        QGraphicsTextItem.__init__(self, str(player_id), parent)
        self.setAcceptDrops(False)
        self.setAcceptHoverEvents(False)

        self.player_id = str(player_id)
        self.setPos((boundary.topLeft()))
        self.setFont(QFont('Calibri', 24))
        self.setDefaultTextColor(QColor(0, 0, 0, 128))

    def paint(self, painter, style, widget=None):
        painter.setBrush(QColor(255, 255, 255, 64))
        painter.drawRect(self.boundingRect())
        QGraphicsTextItem.paint(self, painter, style, widget)
