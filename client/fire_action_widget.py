from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QWidget


class WosFireActionWidget(QWidget):
    location_changed = pyqtSignal(int, int)

    def __init__(self, index, map_size_x, map_size_y, parent=None):
        QWidget.__init__(self, parent)
        self.index = index

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Bomb %s:" % index, self), 0, 0)

        self.attack_x_spinbox = QSpinBox(self)
        self.attack_x_spinbox.blockSignals(True)
        self.attack_x_spinbox.setRange(0, map_size_x - 1)
        self.layout.addWidget(self.attack_x_spinbox, 0, 1)
        self.attack_x_spinbox.valueChanged.connect(self.update_location)
        self.attack_x_spinbox.blockSignals(False)

        self.attack_y_spinbox = QSpinBox(self)
        self.attack_y_spinbox.blockSignals(True)
        self.attack_y_spinbox.setRange(0, map_size_y - 1)
        self.layout.addWidget(self.attack_y_spinbox, 0, 2)
        self.attack_y_spinbox.valueChanged.connect(self.update_location)
        self.attack_y_spinbox.blockSignals(False)

    def get_index(self):
        return self.index

    def get_fire_info(self):
        return self.attack_x_spinbox.value(), self.attack_y_spinbox.value()

    def update_location(self):
        self.location_changed.emit(self.attack_x_spinbox.value(), self.attack_y_spinbox.value())