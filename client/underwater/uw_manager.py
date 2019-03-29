from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client.action_widget import WosActionWidget
from client.underwater.issue_waypoints_dialog import WosIssueWaypointsDialog
import cCommonGame


class WosUwManager(QObject):

    def __init__(self, wos_interface, battle_core_manager, parent=None):
        QObject.__init__(self, parent)
        self.wos_interface = wos_interface
        self.battle_core_manager = battle_core_manager
        self.dialog = None
        self.field_info = self.wos_interface.battlefield.battle_scene.get_field_info()
        self.battle_core_manager.turn_ended.connect(self.end_turn)

    def display_pop_up(self):
        if self.dialog is not None:
            self.dialog.deleteLater()
            self.dialog = None

        self.dialog = WosIssueWaypointsDialog(self.field_info.size.x() - 1, self.field_info.size.y() - 1)
        self.dialog.orders_issued.connect(self.submit_command)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def end_turn(self):
        pass

    def update_action_widget(self):
        actions_widget = self.wos_interface.actions

        widget = QWidget(actions_widget)
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        button = QToolButton(widget)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        button.setText("Command underwater vehicle")
        button.released.connect(self.display_pop_up)
        layout.addWidget(button, 0, 0, 1, 4)

        actions_widget.add_widget(widget, WosActionWidget.WidgetType.ACTION_ADDON)

    def start(self):
        cfg = self.wos_interface.cfg
        if cfg is None or not cfg.en_submarine:
            return

        self.wos_interface.log("Underwater mode is enabled")

        self.update_action_widget()

    def submit_command(self, orders):
        uw_ship_move_info = [cCommonGame.UwShipMovementInfo(8, orders)]
        self.wos_interface.log("Sending orders to underwater vehicle..")
        self.dialog.deleteLater()
        self.dialog = None
        rep = WosClientInterfaceManager().send_action_uw_ops(uw_ship_move_info)
        if rep and rep.ack:
            self.wos_interface.log('Order issued successfully!')
        else:
            self.wos_interface.log(
                "<font color='brown'>Failed! The underwater vehicle is still executing its previous commands.</font>")
