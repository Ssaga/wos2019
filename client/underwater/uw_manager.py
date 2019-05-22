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
import numpy as np
import os


class WosUwManager(QObject):

    def __init__(self, wos_interface, battle_core_manager, parent=None):
        QObject.__init__(self, parent)
        self.wos_interface = wos_interface
        self.battle_core_manager = battle_core_manager
        self.command_dialog = None
        self.report_button = None
        self.report_cache = None
        self.field_info = self.wos_interface.battlefield.battle_scene.get_field_info()

    def display_command_pop_up(self):
        if self.command_dialog is not None:
            self.command_dialog.deleteLater()
            self.command_dialog = None

        self.command_dialog = WosIssueWaypointsDialog(self.field_info.dimension.x() - 1,
                                                      self.field_info.dimension.y() - 1)
        self.command_dialog.orders_issued.connect(self.submit_command)
        self.command_dialog.show()
        self.command_dialog.raise_()
        self.command_dialog.activateWindow()

    def end_turn(self):
        if self.command_dialog is not None:
            self.command_dialog.reject()
            self.command_dialog.deleteLater()
            self.command_dialog = None

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
        report_button.setText("Save Report")
        report_button.setEnabled(False)
        report_button.released.connect(self.save_report)
        layout.addWidget(report_button, 0, 2, 1, 1)
        self.report_button = report_button

        actions_widget.add_widget(widget, WosActionWidget.WidgetType.ACTION_ADDON)

    def update_turn(self):
        rep = WosClientInterfaceManager().get_uw_report(8)
        if rep:
            self.wos_interface.log(vars(rep), cCommonGame.LogType.DEBUG)
        if rep and rep.ack and len(rep.report) > 0:
            self.report_button.setEnabled(True)
            self.report_cache = rep.report
            self.wos_interface.log("You have UW report available")
        else:
            self.report_button.setEnabled(False)

    def save_report(self):
        os.makedirs("uw_report", exist_ok=True)
        np.save("uw_report/latest", self.report_cache)
        self.wos_interface.log("Saved to <a href=\"uw_report\">uw_report/latest.npy</a>")

    def start(self):
        cfg = self.wos_interface.cfg
        if cfg is None or not cfg.en_submarine:
            return
        self.wos_interface.log("UW mode is enabled")
        self.update_action_widget()
        self.battle_core_manager.turn_started.connect(self.update_turn)
        self.battle_core_manager.turn_ended.connect(self.end_turn)

    def submit_command(self, orders):
        self.wos_interface.log("Sending orders to underwater vehicle..")
        self.wos_interface.toggle_overlay(True, 'Sending orders to underwater vehicle..')

        uw_ship_move_info = [cCommonGame.UwShipMovementInfo(8, orders)]
        self.wos_interface.log(orders, cCommonGame.LogType.DEBUG)
        self.command_dialog.deleteLater()
        self.command_dialog = None
        rep = WosClientInterfaceManager().send_action_uw_ops(uw_ship_move_info)
        if rep and rep.ack:
            self.wos_interface.log('Order issued successfully!')
        else:
            self.wos_interface.log(
                "<font color='brown'>Failed! The underwater vehicle is still executing its previous commands.</font>")

        self.wos_interface.toggle_overlay(False)
