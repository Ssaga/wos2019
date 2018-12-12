from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QWidget


class WosActionWidget(QDockWidget):
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent)

        self.setWindowTitle('Action Tool Bar')

        widget = QWidget(self)
        self.setWidget(widget)

        self.layout = QGridLayout(self)
        widget.setLayout(self.layout)

        move_1_combo = QComboBox(self)
        self.layout.addWidget(QLabel('Move 1:'), 0, 0)
        self.layout.addWidget(move_1_combo, 0, 1)

        move_2_combo = QComboBox(self)
        self.layout.addWidget(QLabel('Mov'
                                     'e 2:'), 1, 0)
        self.layout.addWidget(move_2_combo, 1, 1)

        self.layout.addWidget(QLabel('Bomb:'), 2, 0)
        attack_x_combo = QComboBox(self)
        self.layout.addWidget(attack_x_combo, 2, 1)
        attack_y_combo = QComboBox(self)
        self.layout.addWidget(attack_y_combo, 2, 2)

        self.spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(self.spacer)

    def append_widget(self, widget):
        self.layout.removeItem(self.spacer)
        self.layout.addWidget(widget, self.layout.rowCount(), 0, 1, self.layout.columnCount())
        self.layout.addItem(self.spacer)
