from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client.scene_item.battleship_item import WosBattleShipItem
from client.client_interface_manager import WosClientInterfaceManager
from client.phase_manager import WosPhaseManager
from client.ship_info import ShipInfo

import cCommonGame

class WosBattleShipDeploymentManager(WosPhaseManager):
    UPDATE_INTERVAL_IN_MS = 1000

    deployment_ended = pyqtSignal()

    def __init__(self, wos_interface, parent=None):
        WosPhaseManager.__init__(self, wos_interface, parent)
        self.ships_items = []
        self.tools = None
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_game_event)

    def deployment_button_pressed(self):
        self.wos_interface.log("Sending deployment to server..")
        self.sender().setEnabled(False)
        self.deployment_ended.emit()

    def end(self):
        actions_widget = self.wos_interface.actions
        actions_widget.remove_widget(self.tools)
        self.tools.deleteLater()
        self.tools = None
        WosPhaseManager.end(self)

    def send_deployment(self):
        ships = []
        for ship_item in self.ships_items:
            ships.append(ship_item.get_ship_info())
        if WosClientInterfaceManager().send_deployment(ships) or self.wos_interface.is_debug:
            self.wos_interface.log("Server acknowledged")
            self.wos_interface.log("Please wait for all the players to deploy their ships")
            self.update_timer.start(self.UPDATE_INTERVAL_IN_MS)
        else:
            self.wos_interface.log("Server declined")
        # todo; Don't end if server did not acknowledged
        # self.end()

    def start(self):
        self.wos_interface.log("<b>Deployment phase</b>.")
        self.wos_interface.log("Please assign the ships to a desired location in the map. Click and drag the ships to "
                               "reposition with left mouse button, rotate the ships with right mouse button.")

        scene = self.wos_interface.battlefield.battle_scene.scene()
        cfg = self.wos_interface.cfg
        map_size_x = 120
        map_size_y = 120
        if cfg is not None:
            map_size_x = cfg.map_size.x
            map_size_y = cfg.map_size.y

        self.wos_interface.battlefield.generate_scene(map_size_x, map_size_y)
        field_info = self.wos_interface.battlefield.battle_scene.get_field_info()

        # todo: Read config file for squad list, stub for now
        self.ships_items = [WosBattleShipItem(field_info, 0, 2), WosBattleShipItem(field_info, 1, 2),
                            WosBattleShipItem(field_info, 2, 3), WosBattleShipItem(field_info, 3, 3),
                            WosBattleShipItem(field_info, 4, 4), WosBattleShipItem(field_info, 5, 4),
                            WosBattleShipItem(field_info, 6, 5), WosBattleShipItem(field_info, 7, 5)]

        # todo: Need to get boundary from config
        start_position = cCommonGame.Position()
        if self.wos_interface.player_info.player_id == 2:
            start_position.y += 60
        elif self.wos_interface.player_info.player_id == 3:
            start_position.y += 60
        elif self.wos_interface.player_info.player_id == 4:
            start_position.x += 60
            start_position.y += 60

        for i in range(0, len(self.ships_items)):
            scene.addItem(self.ships_items[i])
            self.ships_items[i].set_ship_type(ShipInfo.Type.FRIENDLY)
            self.ships_items[i].set_grid_position(start_position.x + i, start_position.y + 0)

        self.update_action_widget()

        self.deployment_ended.connect(self.send_deployment)

    def update_action_widget(self):
        actions_widget = self.wos_interface.actions

        self.tools = QWidget(actions_widget)
        layout = QVBoxLayout(self.tools)
        self.tools.setLayout(layout)

        deployment_button = QToolButton(self.tools)
        deployment_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        deployment_button.setText("Confirm Deployment")
        deployment_button.released.connect(self.deployment_button_pressed)
        layout.addWidget(deployment_button)

        actions_widget.append_widget(self.tools)

    def update_game_event(self):
        turn_info = WosClientInterfaceManager().get_turn_info()
        if turn_info:
            self.end()
        else:
            self.update_timer.start()
