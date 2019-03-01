from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client.action_widget import WosActionWidget
from client.battle_util import WosBattleUtil
from client.client_interface_manager import WosClientInterfaceManager
from client.ship_info import ShipInfo
import cCommonGame


class WosSatelliteEo2Manager(QObject):

    def __init__(self, wos_interface, battle_core_manager, parent=None):
        QObject.__init__(self, parent)
        self.wos_interface = wos_interface
        self.battle_core_manager = battle_core_manager
        self.dialog = None

        self.battle_core_manager.turn_ended.connect(self.end_turn)

    def display_pop_up(self):
        if self.dialog is not None:
            self.dialog.deleteLater()
            self.dialog = None

        self.dialog = self.make_pop_up_dialog()
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def end_turn(self):
        pass

    def make_pop_up_dialog(self):
        dialog = QDialog(self.wos_interface.main_window())
        dialog.setWindowTitle('Please input the 6 parameter')
        dialog.setMinimumWidth(50)
        dialog.accepted.connect(self.submit_command)
        dialog.text_list = []

        default_text = [6378 + 2000, 0, 5, 0, 150, 0]

        layout = QGridLayout(dialog)
        dialog.setLayout(layout)

        dbl_validator = QDoubleValidator()
        for i in range(0, 6):
            layout.addWidget(QLabel("%s:" % i), i, 0)
            line_edit = QLineEdit()
            line_edit.setValidator(dbl_validator)
            line_edit.setText(str(default_text[i]))
            layout.addWidget(line_edit, i, 1)
            dialog.text_list.append(line_edit)

        dialog.checkbox = QCheckBox('Is Right', dialog)
        layout.addWidget(dialog.checkbox, 6, 0, 1, 2)

        submit_button = QToolButton(dialog)
        submit_button.setText("Send")
        submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        submit_button.released.connect(dialog.accept)
        layout.addWidget(submit_button, 7, 0, 1, 2)

        return dialog

    def update_action_widget(self):
        actions_widget = self.wos_interface.actions

        widget = QWidget(actions_widget)
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        eo_button = QToolButton(widget)
        eo_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        eo_button.setText("Send EO Satellite 2")
        eo_button.released.connect(self.display_pop_up)
        layout.addWidget(eo_button, 0, 0, 1, 3)

        actions_widget.add_widget(widget, WosActionWidget.WidgetType.ACTION_ADDON)

    def start(self):
        cfg = self.wos_interface.cfg
        if cfg is None or not cfg.en_satellite_func2:
            return

        self.wos_interface.log("EO Satellite mode 2 is enabled")

        self.update_action_widget()

    def submit_command(self):
        satcom = cCommonGame.SatcomInfo()
        satcom.a = float(self.dialog.text_list[0].text())
        satcom.e = float(self.dialog.text_list[1].text())
        satcom.i = float(self.dialog.text_list[2].text())
        satcom.om = float(self.dialog.text_list[3].text())
        satcom.Om = float(self.dialog.text_list[4].text())
        satcom.M = float(self.dialog.text_list[5].text())
        satcom.is_enable = True
        satcom.is_rhs = False
        satcom.is_rhs = (self.dialog.checkbox.checkState() == Qt.Checked)
        self.wos_interface.log("Sending EO satellite 2..")
        self.dialog.deleteLater()
        self.dialog = None
        rep = WosClientInterfaceManager().send_action_satcom(satcom)
        if rep and rep.ack:
            self.wos_interface.log('Success!')
            turn_info = WosClientInterfaceManager().get_turn_info()
            # Handle case where update_turn was wrongly called
            if turn_info and turn_info.ack:
                for i in range(0, len(turn_info.other_ship_list)):
                    WosBattleUtil.insert_ship_to_scene(self.wos_interface.battlefield.battle_scene,
                                                       turn_info.other_ship_list[i], ShipInfo.Type.UNKNOWN)
                self.wos_interface.battlefield.update_map(turn_info.map_data)
        else:
            self.wos_interface.log("<font color='brown'>Failed! Only 1 satcom action per turn.</font>")
