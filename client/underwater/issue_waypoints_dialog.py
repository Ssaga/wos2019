from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QVBoxLayout
from client.icon_push_button import WosIconPushButton
from client.underwater.waypoint_action_widget import WosWaypointActionWidget
import cCommonGame
import qtawesome


class WosIssueWaypointsDialog(QDialog):
    DEFAULT_NUMBER_OF_WAYPOINTS = 1

    orders_issued = pyqtSignal(list)

    def __init__(self, map_size_x, map_size_y, parent=None):
        QDialog.__init__(self, parent)
        self.map_size_x = map_size_x
        self.map_size_y = map_size_y

        self.setWindowTitle('Issue UW Vehicle command')
        self.setMinimumWidth(450)
        self.accepted.connect(self.collect_orders)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.layout.waypoint_layout = QVBoxLayout(self)
        self.layout.addLayout(self.layout.waypoint_layout, 0, 0)
        for i in range(0, self.DEFAULT_NUMBER_OF_WAYPOINTS):
            self.add_new_waypoint()

        add_waypoint_button = WosIconPushButton(qtawesome.icon('fa.plus-square-o'), qtawesome.icon('fa.plus-square'),
                                                self)
        add_waypoint_button.setToolTip('Add Waypoint')
        add_waypoint_button.released.connect(self.add_new_waypoint)
        self.layout.addWidget(add_waypoint_button, 1, 0)
        self.layout.setAlignment(add_waypoint_button, Qt.AlignRight)

        self.layout.addItem(QSpacerItem(2, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        submit_button = QToolButton(self)
        submit_button.setText("Send")
        submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        submit_button.released.connect(self.accept)
        self.layout.addWidget(submit_button, 3, 0)

    def add_new_waypoint(self):
        index = self.layout.waypoint_layout.count()
        waypoint_widget = WosWaypointActionWidget(index, self.map_size_x, self.map_size_y, self)
        waypoint_widget.waypoint_remove_pressed.connect(self.delete_waypoint)
        self.layout.waypoint_layout.addWidget(waypoint_widget)

    def delete_waypoint(self, index):
        # Update waypoint widget index assuming the waypoint is already deleted
        new_index = 0
        for i in range(0, self.layout.waypoint_layout.count()):
            if index == i:
                continue
            waypoint_widget = self.layout.waypoint_layout.itemAt(i).widget()
            waypoint_widget.set_index(new_index)
            new_index += 1

        # Delete waypoint
        waypoint_widget = self.layout.waypoint_layout.itemAt(index).widget()
        self.layout.waypoint_layout.removeWidget(waypoint_widget)
        waypoint_widget.deleteLater()

    def collect_orders(self):
        orders = list()
        for i in range(0, self.layout.waypoint_layout.count()):
            waypoint_widget = self.layout.waypoint_layout.itemAt(i).widget()
            waypoint_info = waypoint_widget.get_waypoint_info()
            orders.append(cCommonGame.UwActionMoveScan(cCommonGame.Position(waypoint_info[0], waypoint_info[1]),
                                                       waypoint_info[2]))
        self.orders_issued.emit(orders)
