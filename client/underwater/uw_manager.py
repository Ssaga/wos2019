from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client.action_widget import WosActionWidget
from client.client_interface_manager import WosClientInterfaceManager
from client.underwater.issue_waypoints_dialog import WosIssueWaypointsDialog
import cCommonGame


class WosUwManager(QObject):

    def __init__(self, wos_interface, battle_core_manager, parent=None):
        QObject.__init__(self, parent)
        self.wos_interface = wos_interface
        self.battle_core_manager = battle_core_manager
        self.command_dialog = None
        self.report_dialog = None
        self.field_info = self.wos_interface.battlefield.battle_scene.get_field_info()
        self.battle_core_manager.turn_ended.connect(self.end_turn)

    def display_command_pop_up(self):
        if self.command_dialog is not None:
            self.command_dialog.deleteLater()
            self.command_dialog = None

        self.command_dialog = WosIssueWaypointsDialog(self.field_info.size.x() - 1, self.field_info.size.y() - 1)
        self.command_dialog.orders_issued.connect(self.submit_command)
        self.command_dialog.show()
        self.command_dialog.raise_()
        self.command_dialog.activateWindow()

    def display_report_pop_up(self):
        if self.report_dialog is not None:
            self.report_dialog.deleteLater()
            self.report_dialog = None

        rep = WosClientInterfaceManager().get_uw_report(8)
        if rep and rep.ack:
            self.wos_interface.log(rep)
        else:
            self.wos_interface.log('No report to retrieve.')

        # self.report_dialog = WosIssueWaypointsDialog(self.field_info.size.x() - 1, self.field_info.size.y() - 1)
        # self.report_dialog.orders_issued.connect(self.submit_command)
        # self.report_dialog.show()
        # self.report_dialog.raise_()
        # self.report_dialog.activateWindow()

    def end_turn(self):
        pass

    def update_action_widget(self):
        actions_widget = self.wos_interface.actions

        widget = QWidget(actions_widget)
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        layout.addWidget(QLabel('Underwater Vehicle:'), 0, 0, 1, 1)

        command_button = QToolButton(widget)
        command_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        command_button.setText("Command")
        command_button.released.connect(self.display_command_pop_up)
        layout.addWidget(command_button, 0, 1, 1, 1)

        report_button = QToolButton(widget)
        report_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        report_button.setText("View Report")
        report_button.released.connect(self.display_report_pop_up)
        layout.addWidget(report_button, 0, 2, 1, 1)

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
        self.command_dialog.deleteLater()
        self.command_dialog = None
        rep = WosClientInterfaceManager().send_action_uw_ops(uw_ship_move_info)
        if rep and rep.ack:
            self.wos_interface.log('Order issued successfully!')
        else:
            self.wos_interface.log(
                "<font color='brown'>Failed! The underwater vehicle is still executing its previous commands.</font>")
