from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client.action_widget import WosActionWidget
from client.client_interface_manager import WosClientInterfaceManager
from client.phase_manager import WosPhaseManager
from client.scene_item.battleship_item import WosBattleShipItem
from client.scene_item.underwater_ship_item import WosUnderwaterShipItem
from client.ship_info import ShipInfo
import cCommonGame
import copy
import numpy as np


class WosBattleShipDeploymentManager(WosPhaseManager):
    UPDATE_INTERVAL_IN_MS = 1000

    deployment_ended = pyqtSignal(QToolButton)

    def __init__(self, wos_interface, parent=None):
        WosPhaseManager.__init__(self, wos_interface, parent)
        self.ships_items = []
        self.ship_uw_items = []
        self.tools = None
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_game_event)
        self.update_timer.start(self.UPDATE_INTERVAL_IN_MS)

    def clean_up(self):
        self.update_timer.timeout.disconnect(self.update_game_event)
        self.update_timer.stop()
        if self.tools is not None:
            self.tools.deleteLater()

    def deployment_button_pressed(self):
        self.wos_interface.log("Sending deployment to server..")
        self.sender().setEnabled(False)
        self.deployment_ended.emit(self.sender())

    def end(self):
        self.update_timer.stop()
        if self.tools is not None:
            actions_widget = self.wos_interface.actions
            actions_widget.remove_widget(self.tools)
            self.tools.deleteLater()
            self.tools = None
        WosPhaseManager.end(self)

    def send_deployment(self, deployment_button):
        ships = list()
        for ship_item in self.ships_items:
            ships.append(ship_item.get_ship_info())
        ships_uw = list()
        for ship_item in self.ship_uw_items:
            ships_uw.append(ship_item.get_ship_info())

        if WosClientInterfaceManager().send_deployment(ships, ships_uw) or self.wos_interface.is_debug:
            self.wos_interface.log("Server acknowledged")
            self.wos_interface.log("Please wait for all the players to deploy their ships")
            for ship_item in self.ships_items:
                ship_item.set_is_draggable(False)
            for ship_item in self.ship_uw_items:
                ship_item.set_is_draggable(False)
        else:
            self.wos_interface.log(
                "<font color='brown'>Server declined, please check that your deployments are valid</font>")
            deployment_button.setEnabled(True)
        # todo; Don't end if server did not acknowledged
        # self.end()

    def set_ship_position(self, ship, xpos=-1, ypos=-1):
        if xpos >= 0 and ypos >= 0:
            ship.set_grid_position(xpos, ypos)
        else:
            while True:
                boundary = self.wos_interface.cfg.boundary[str(self.wos_interface.player_info.player_id)]
                # Magic number 3 to prevent out of bound for the longest ship
                xpos = np.random.randint(boundary.min_x + 3, boundary.max_x - 3)
                ypos = np.random.randint(boundary.min_y + 3, boundary.max_y - 3)
                ship.set_grid_position(xpos, ypos)
                # np.random.randint(0, 5) returns 0 to 4 inclusive
                num_of_rotation = np.random.randint(0, 5)
                # range(0,4) will loop from 0 to 3 inclusive
                for i in range(0, num_of_rotation):
                    ship.rotate_ship()
                # Perform check(inefficient one) on whether ship has collided with other objects on the map
                ships_items = copy.copy(self.ships_items)
                if ship in ships_items:
                    ships_items.remove(ship)
                if self.wos_interface.battlefield.is_locations_accessible(ship.ship_info.get_placement(), ships_items):
                    break

    def start(self):
        rep = WosClientInterfaceManager().register_player()
        if not rep and not self.wos_interface.is_debug:
            return

        self.wos_interface.log("<b>Deployment phase</b>.")
        self.wos_interface.log("Please assign the ships to a desired location in the map. Click and drag the ships to "
                               "reposition with left mouse button, rotate the ships with right mouse button.")

        cfg = self.wos_interface.cfg
        self.wos_interface.battlefield.battle_scene.update_boundaries(cfg.boundary)
        player_id = str(self.wos_interface.player_info.player_id)
        player_boundary = self.wos_interface.cfg.boundary[player_id]

        if rep:
            self.wos_interface.battlefield.update_map(rep.map_data)

        field_info = self.wos_interface.battlefield.battle_scene.get_field_info()

        # todo: Read config file for squad list, stub for now
        self.ships_items = [WosBattleShipItem(field_info, player_boundary, 0, 2),
                            WosBattleShipItem(field_info, player_boundary, 1, 2),
                            WosBattleShipItem(field_info, player_boundary, 2, 3),
                            WosBattleShipItem(field_info, player_boundary, 3, 3),
                            WosBattleShipItem(field_info, player_boundary, 4, 4),
                            WosBattleShipItem(field_info, player_boundary, 5, 4),
                            WosBattleShipItem(field_info, player_boundary, 6, 5),
                            WosBattleShipItem(field_info, player_boundary, 7, 5)]
        if self.wos_interface.cfg.en_submarine:
            self.ship_uw_items = [WosUnderwaterShipItem(field_info, player_boundary, 8)]

        scene = self.wos_interface.battlefield.battle_scene.scene()
        start_position = cCommonGame.Position()
        start_position.x = player_boundary.min_x
        start_position.y = player_boundary.min_y
        cnt = 0
        for i in range(0, len(self.ships_items)):
            scene.addItem(self.ships_items[i])
            self.ships_items[i].set_ship_type(ShipInfo.Type.FRIENDLY)
            # self.ships_items[i].set_grid_position(start_position.x + i, start_position.y + 2)
            self.set_ship_position(self.ships_items[i])
            cnt += 1
        for i in range(0, len(self.ship_uw_items)):
            scene.addItem(self.ship_uw_items[i])
            self.ship_uw_items[i].set_ship_type(ShipInfo.Type.FRIENDLY)
            # self.ship_uw_items[i].set_grid_position(start_position.x + cnt, start_position.y + 2)
            self.set_ship_position(self.ship_uw_items[i])
            cnt += 1

        self.wos_interface.battlefield.battle_scene.centerOn(self.ships_items[-1])

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

        actions_widget.add_widget(self.tools, WosActionWidget.WidgetType.ACTION_CORE)

    def update_game_event(self):
        turn_info = WosClientInterfaceManager().get_turn_info()
        if turn_info:
            self.end()
        else:
            self.update_timer.start()
