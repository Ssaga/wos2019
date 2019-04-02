from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon


class WosIconPushButton(QPushButton):

    def __init__(self, icon, icon_hover=QIcon(), parent=None):
        QPushButton.__init__(self, icon, '', parent)
        self.icon = icon
        self.icon_hover = icon_hover
        self.setStyleSheet('QPushButton{border:none;background-color:rgba(0, 0, 0, 0);}')
        self.setIconSize(QSize(20, 20))
        self.setMinimumSize(20, 20)
        self.setMaximumSize(20, 20)

    def enterEvent(self, event):
        self.setIcon(self.icon_hover)

    def leaveEvent(self, event):
        self.setIcon(self.icon)

    def mousePressEvent(self, event):
        self.setIconSize(QSize(17, 17))
        super(WosIconPushButton, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setIconSize(QSize(20, 20))
        super(WosIconPushButton, self).mouseReleaseEvent(event)
