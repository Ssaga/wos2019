from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget


class WosTimeWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.default_string = '--'

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel('Time Left:'), 0, 0)

        self.time_text = QLabel(self.default_string, self)

        self.layout.addWidget(self.time_text, 0, 1)

    @staticmethod
    def format_time(t):
        return "%s seconds" % (str(round(t)),)

    def set_time(self, t):
        t = WosTimeWidget.format_time(t)
        self.time_text.setText(t)

    def setEnabled(self, b):
        # self.time_text.setText(self.default_string)
        QWidget.setEnabled(self, b)
