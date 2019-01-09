from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client.client_interface_manager import WosClientInterfaceManager
from client.fire_action_widget import WosFireActionWidget
from client.move_action_widget import WosMoveActionWidget
from client.phase_manager import WosPhaseManager
from client.scene_item.battleship_item import WosBattleShipItem
from client.scene_item.fire_annotation_item import WosFireAnnotationItem
from client.ship_info import ShipInfo
import cCommonGame


class WosBattleManager(WosPhaseManager):
    UPDATE_INTERVAL_IN_MS = 1000

    deployment_ended = pyqtSignal()

    def __init__(self, wos_interface, parent=None):
        WosPhaseManager.__init__(self, wos_interface, parent)
        self.current_player_turn = 0
        self.current_player_round = 0
        self.field_info = None
        self.num_fire_actions = 1
        self.num_move_actions = 2
        self.num_sat_actions = 1
        self.map_size_x = 120
        self.map_size_y = 120
        self.fire_action_widgets = list()
        self.move_action_widgets = list()
        self.ships_items = dict()
        self.ships_shadow_items = dict()
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_game_event)

    def insert_ship_to_scene(self, scene, ship_info, ship_type):
        ship_item = WosBattleShipItem(self.field_info, ship_info.ship_id, ship_info.size, ship_info.is_sunken)
        ship_item.set_grid_position(ship_info.position.x, ship_info.position.y)
        ship_item.set_heading(ship_info.heading)
        ship_item.set_ship_type(ship_type)
        ship_item.set_is_draggable(False)
        scene.addItem(ship_item)
        return ship_item

    def insert_annotations_to_scene(self, scene):
        for widget in self.move_action_widgets:
            ship_shadow = self.ships_items[0].clone()
            scene.addItem(ship_shadow)
            self.ships_shadow_items[widget.get_index()] = ship_shadow
            widget.combo_updated.connect(self.update_ship_shadow)
        self.update_ship_shadow()

        for widget in self.fire_action_widgets:
            x, y = widget.get_fire_info()
            fire = WosFireAnnotationItem(self.field_info, "Bomb %s" % widget.get_index(), x, y)
            widget.location_changed.connect(fire.set_position)
            scene.addItem(fire)

    def update_ship_shadow(self):
        for widget in self.move_action_widgets:
            ship_id, action = widget.get_move_info()
            ship = self.ships_items[ship_id]
            ship_shadow = self.ships_shadow_items[widget.get_index()]
            ship.make_shadow(ship_shadow, action)
            ship_shadow.update()

    def is_current_turn(self, game_status):
        return game_status.player_turn == self.wos_interface.player_info.player_id

    def start(self):
        self.wos_interface.log("<b>Battle phase</b>.")
        self.update_configurations()
        self.update_action_widget()
        self.update_timer.start(self.UPDATE_INTERVAL_IN_MS)

    def update_action_widget(self):
        actions_widget = self.wos_interface.actions

        widget = QWidget(actions_widget)
        layout = QGridLayout(widget)
        widget.setLayout(layout)

        form_row = 0

        for i in range(1, self.num_move_actions + 1):
            move_action_widget = WosMoveActionWidget(i)
            layout.addWidget(move_action_widget, form_row, 0, 1, 3)
            self.move_action_widgets.append(move_action_widget)
            form_row += 1

        for i in range(1, self.num_fire_actions + 1):
            fire_action_widget = WosFireActionWidget(i, self.map_size_x, self.map_size_y)
            layout.addWidget(fire_action_widget, form_row, 0, 1, 3)
            self.fire_action_widgets.append(fire_action_widget)
            form_row += 1

        submit_button = QToolButton(widget)
        submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        submit_button.setText("End Turn")
        submit_button.released.connect(self.submit_button_pressed)
        layout.addWidget(submit_button, form_row, 0, 1, 3)

        actions_widget.append_widget(widget)

        actions_widget.setEnabled(False)

    def update_configurations(self):
        cfg = self.wos_interface.cfg
        if cfg is not None:
            self.num_fire_actions = cfg.num_of_fire_act
            self.num_move_actions = cfg.num_of_move_act
            self.num_sat_actions = cfg.num_of_satc_act
            self.map_size_x = cfg.map_size.x
            self.map_size_y = cfg.map_size.y

    def update_turn(self):
        turn_info = WosClientInterfaceManager().get_turn_info()
        # Handle case where update_turn was wrongly called
        if not turn_info or not turn_info.ack:
            self.update_timer.start()
            return

        self.wos_interface.log('Your turn, please issue your commands')

        scene = self.wos_interface.battlefield.battle_scene.scene()
        self.wos_interface.battlefield.update_map(turn_info.map_data)
        self.field_info = self.wos_interface.battlefield.battle_scene.get_field_info()

        self.ships_items = dict()
        for i in range(0, len(turn_info.self_ship_list)):
            ship_item = self.insert_ship_to_scene(scene, turn_info.self_ship_list[i], ShipInfo.Type.FRIENDLY)
            if ship_item is not None:
                ship_id = ship_item.ship_info.ship_id
                self.ships_items[ship_id] = ship_item

        for i in range(0, len(turn_info.enemy_ship_list)):
            self.insert_ship_to_scene(scene, turn_info.enemy_ship_list[i], ShipInfo.Type.HOSTILE)

        for i in range(0, len(turn_info.other_ship_list)):
            self.insert_ship_to_scene(scene, turn_info.other_ship_list[i], ShipInfo.Type.UNKNOWN)

        for widget in self.move_action_widgets:
            widget.update_move_ship_combo(self.ships_items)

        self.insert_annotations_to_scene(self.wos_interface.battlefield.battle_scene.scene())

        self.wos_interface.actions.setEnabled(True)

        # Display turn info in log, except for map_data
        turn_info_visual = vars(turn_info)
        turn_info_visual.pop('map_data', None)
        self.wos_interface.log(turn_info_visual, cCommonGame.LogType.DEBUG)

    def submit_button_pressed(self):
        actions_widget = self.wos_interface.actions
        actions_widget.setEnabled(False)

        # Collate move action(s)
        move_list = list()
        for widget in self.move_action_widgets:
            ship_id, action = widget.get_move_info()
            move_info = cCommonGame.ShipMovementInfo(ship_id, action)
            move_list.append(move_info)
            self.wos_interface.log(move_info.to_string())

        # Collate fire action(s)
        fire_list = list()
        for widget in self.fire_action_widgets:
            x, y = widget.get_fire_info()
            fire_info = cCommonGame.FireInfo(cCommonGame.Position(x, y))
            fire_list.append(fire_info)
            self.wos_interface.log(fire_info.to_string())

        self.wos_interface.log("Sending commands to server..")
        # Consider doing validations
        WosClientInterfaceManager().send_action_move(move_list)
        WosClientInterfaceManager().send_action_attack(fire_list)
        self.wos_interface.log("Sent")

        self.update_timer.start()

    def update_game_event(self):
        game_status = WosClientInterfaceManager().get_game_status()
        if game_status is not None:
            if self.current_player_turn != game_status.player_turn:
                self.current_player_turn = game_status.player_turn
                self.current_player_round = game_status.game_round
                self.wos_interface.log(
                    "Round %s: Player %s turn" % (game_status.game_round, game_status.player_turn))

            if self.is_current_turn(game_status):
                self.update_turn()
            else:
                # Update event again in x seconds time
                self.update_timer.start()
