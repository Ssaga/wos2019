from PyQt5.QtCore import Qt, QPointF, QRect
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPalette, QPen
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget
import math

'''@class
This widget creates a translucent overlay over its parent widget and draws a loading icon and message
'''


class LoadingOverlayWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        self.text = 'Please wait...'
        self.timer = None
        self.counter = 0

    def closeEvent(self, event):
        self.killTimer(self.timer)

    def paintEvent(self, event):
        # Resize to parent
        width = self.parent.width()
        height = self.parent.height()
        self.setGeometry(0, 0, width, height)

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.fillRect(QRect(0, 0, width, height), QBrush(QColor(0, 0, 0, 168)))

        painter.setPen(QPen(QColor(255, 255, 255)))
        # Draw loading icon
        for i in range(6):
            if self.counter % 6 == i or self.counter % 6 == ((i + 1) % 6):
                painter.setBrush(QBrush(QColor(255, 127, 127)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))

            painter.drawEllipse(
                width / 2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                height / 2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                20, 20)

        # Draw loading message
        painter.setFont(QFont("", 25, QFont.Bold))
        painter.drawText(QRect(0, height / 2 + 30 * math.sin(2 * math.pi * 2 / 6.0) + 25, width, 50), Qt.AlignCenter,
                         self.text)

        painter.end()

    def set_text(self, text):
        self.text = text

    def showEvent(self, event):
        self.resize(self.parent.size())
        self.timer = self.startTimer(100)
        self.counter = 0
        self.raise_()
        self.update()
        # Not correct to use this but I'm too lazy to refactor all the necessary functions in a QThread
        QCoreApplication.processEvents()

    def timerEvent(self, event):
        self.raise_()
        self.counter = (self.counter + 1) % 6
        self.update()
        QCoreApplication.processEvents()
