from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QWidget
from client.icon_push_button import WosIconPushButton
import qtawesome


class WosWaypointActionWidget(QWidget):
    waypoint_changed = pyqtSignal(int, int, int, int)
    waypoint_remove_pressed = pyqtSignal(int)

    def __init__(self, index, map_size_x, map_size_y, parent=None):
        QWidget.__init__(self, parent)
        self.index = index

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.waypoint_label = QLabel("Waypoint %s:" % index, self)
        self.layout.addWidget(self.waypoint_label, 0, 0)

        self.waypoint_x_spinbox = QSpinBox(self)
        self.waypoint_x_spinbox.blockSignals(True)
        self.waypoint_x_spinbox.setRange(0, map_size_x)
        self.layout.addWidget(self.waypoint_x_spinbox, 0, 1)
        self.waypoint_x_spinbox.valueChanged.connect(self.update_waypoint)
        self.waypoint_x_spinbox.blockSignals(False)

        self.waypoint_y_spinbox = QSpinBox(self)
        self.waypoint_y_spinbox.blockSignals(True)
        self.waypoint_y_spinbox.setRange(0, map_size_y)
        self.layout.addWidget(self.waypoint_y_spinbox, 0, 2)
        self.waypoint_y_spinbox.valueChanged.connect(self.update_waypoint)
        self.waypoint_y_spinbox.blockSignals(False)

        self.layout.addWidget(QLabel("Duration: ", self), 0, 3)
        self.duration_spinbox = QSpinBox(self)
        self.duration_spinbox.blockSignals(True)
        self.duration_spinbox.setRange(0, 10)
        self.layout.addWidget(self.duration_spinbox, 0, 4)
        self.duration_spinbox.valueChanged.connect(self.update_waypoint)
        self.duration_spinbox.blockSignals(False)

        self.remove_button = WosIconPushButton(qtawesome.icon('fa.minus-square-o'), qtawesome.icon('fa.minus-square'),
                                               self)
        self.remove_button.setToolTip('Remove Waypoint %s' % self.index)
        self.remove_button.released.connect(self.remove_button_pressed)
        self.layout.addWidget(self.remove_button, 0, 5)

    def get_index(self):
        return self.index

    def get_waypoint_info(self):
        return int(self.waypoint_x_spinbox.value()), int(self.waypoint_y_spinbox.value()), int(
            self.duration_spinbox.value())

    def set_index(self, index):
        self.index = index
        self.waypoint_label.setText("Waypoint %s:" % index)
        self.remove_button.setToolTip('Remove Waypoint %s' % self.index)

    def remove_button_pressed(self):
        self.waypoint_remove_pressed.emit(self.index)

    def update_waypoint(self):
        self.waypoint_changed.emit(self.index, self.waypoint_x_spinbox.value(), self.waypoint_y_spinbox.value(),
                                   self.duration_spinbox.value())
