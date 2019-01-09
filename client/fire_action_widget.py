from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

import cCommonGame


class WosFireActionWidget(QWidget):
    location_changed = pyqtSignal(int, int)

    def __init__(self, index, map_size_x, map_size_y, parent=None):
        QWidget.__init__(self, parent)
        self.index = index

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Bomb %s:" % index, self), 0, 0)

        self.attack_x_combo = QComboBox(self)
        self.attack_x_combo.blockSignals(True)
        for i in range(0, map_size_x):
            self.attack_x_combo.addItem(str(i), i)
            self.layout.addWidget(self.attack_x_combo, 0, 1)
        self.attack_x_combo.currentTextChanged.connect(self.update_location)
        self.attack_x_combo.blockSignals(False)

        self.attack_y_combo = QComboBox(self)
        self.attack_y_combo.blockSignals(True)
        for i in range(0, map_size_y):
            self.attack_y_combo.addItem(str(i), i)
        self.layout.addWidget(self.attack_y_combo, 0, 2)
        self.attack_y_combo.currentTextChanged.connect(self.update_location)
        self.attack_y_combo.blockSignals(False)
        
    def update_location(self):
        self.location_changed.emit(self.attack_x_combo.currentData(), self.attack_y_combo.currentData())

    def get_index(self):
        return self.index

    def get_fire_info(self):
        return self.attack_x_combo.currentData(), self.attack_y_combo.currentData()