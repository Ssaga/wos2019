from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from client.client_interface_manager import WosClientInterfaceManager
from client.phase_manager import WosPhaseManager
from client.wos import PlayerInfo
import cCommonGame


class WosCreationManager(WosPhaseManager):
    deployment_ended = pyqtSignal()

    def __init__(self, wos_interface, parent=None):
        WosPhaseManager.__init__(self, wos_interface, parent)
        self.dialog = None
        # todo: Read from config file or get from server
        self.num_of_players = 8

    def register_player(self, player_id):
        self.wos_interface.log("Creating player with ID: %s.." % player_id)
        is_success = WosClientInterfaceManager().connect_to_server(player_id)
        if is_success or self.wos_interface.is_debug:
            self.wos_interface.player_info = PlayerInfo(player_id)
            self.wos_interface.cfg = WosClientInterfaceManager().get_config()
            self.wos_interface.log("<font color='green'>Success! You are player: <b>%s</b></font>" % player_id)
            self.wos_interface.log(vars(self.wos_interface.cfg), cCommonGame.LogType.DEBUG)
            self.wos_interface.window.setWindowTitle("World Of Science: Battleship (Player %s)" % player_id)
        else:
            self.wos_interface.log(
                "<font color='red'>Fail to connect to server / register player with ID: %s</font>" % player_id)
            self.wos_interface.log(
                "<font color='red'>Please restart the game</font>")

        return is_success

    def start(self):
        if 'player_id' in self.wos_interface.client_cfg and 1 <= self.wos_interface.client_cfg['player_id'] <= 8:
            is_success = self.register_player(self.wos_interface.client_cfg['player_id'])
            if is_success or self.wos_interface.is_debug:
                self.end()
        else:
            self.dialog = QDialog(self.wos_interface.main_window(), Qt.WindowTitleHint)
            self.dialog.setWindowTitle('Please Select An ID')
            self.dialog.setMinimumWidth(250)
            self.dialog.accepted.connect(self.submit_button_pressed)

            layout = QGridLayout(self.dialog)
            self.dialog.setLayout(layout)
            layout.addWidget(QLabel('Player ID:'), 0, 0)
            self.dialog.combo = QComboBox(self.dialog)
            self.dialog.combo.setObjectName('id_combo')
            for i in range(1, self.num_of_players + 1):
                self.dialog.combo.addItem(str(i), i)
            layout.addWidget(self.dialog.combo, 0, 1)

            submit_button = QToolButton(self.dialog)
            submit_button.setText("Submit")
            submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            submit_button.released.connect(self.dialog.accept)
            layout.addWidget(submit_button, 1, 0, 1, 2)

            self.dialog.show()
            self.dialog.raise_()
            self.dialog.activateWindow()

    def submit_button_pressed(self):
        player_id = self.dialog.combo.currentData()
        is_success = self.register_player(player_id)
        if is_success or self.wos_interface.is_debug:
            self.dialog.deleteLater()
            self.dialog = None
            self.end()
        else:
            self.dialog.show()
            self.dialog.raise_()
            self.dialog.activateWindow()
