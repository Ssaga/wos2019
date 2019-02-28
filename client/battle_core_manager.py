from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client.action_widget import WosActionWidget
from client.client_interface_manager import WosClientInterfaceManager
from client.fire_action_widget import WosFireActionWidget
from client.move_action_widget import WosMoveActionWidget
from client.scene_item.battleship_item import WosBattleShipItem
from client.scene_item.fire_annotation_item import WosFireAnnotationItem
from client.ship_info import ShipInfo
from client.time_widget import WosTimeWidget
import cCommonGame


class WosBattleCoreManager(QObject):
    UPDATE_INTERVAL_IN_MS = 1000

    def __init__(self, wos_interface, parent=None):
        QObject.__init__(self, parent)
        self.wos_interface = wos_interface
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
        self.ships_friendly_items = dict()
        self.ships_other_items = list()
        self.ships_hostile_items = list()
        self.ships_shadow_items = dict()
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_game_event_parallel)
        self.time_widget = None

    def end_turn(self):
        self.time_widget.setEnabled(False)
        self.wos_interface.actions.setEnabled(False)

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
            ship_shadow = self.ships_friendly_items[0].clone()
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
        moves = dict()
        ship_shadows = dict()
        # For every ship, get all the actions to be taken and store them in a list (as one ship can perform more than
        # one action per turn)
        for widget in self.move_action_widgets:
            ship_id, action = widget.get_move_info()
            moves.setdefault(ship_id, [])
            moves[ship_id].append(action)
            ship_shadows.setdefault(ship_id, [])
            ship_shadows[ship_id].append(self.ships_shadow_items[widget.get_index()])

        for ship_id, actions in moves.items():
            ship = self.ships_friendly_items[ship_id]
            ship_shadow = ship_shadows[ship_id][0]
            ship.make_shadow(ship_shadow, actions)
            ship_shadow.show()
            ship_shadow.update()
            # When one ship contains more than one action, we hide any outstanding shadows
            for i in range(1, len(ship_shadows[ship_id])):
                ship_shadows[ship_id][i].hide()

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
        layout.setContentsMargins(0, 0, 0, 0)
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

        actions_widget.add_widget(widget, WosActionWidget.WidgetType.ACTION_CORE)

        submit_button = QToolButton(widget)
        submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        submit_button.setText("End Turn")
        submit_button.released.connect(self.submit_button_pressed)
        actions_widget.add_widget(submit_button, WosActionWidget.WidgetType.COMMAND)
        form_row += 1

        self.time_widget = WosTimeWidget(widget)
        actions_widget.add_widget(self.time_widget, WosActionWidget.WidgetType.AFTER_SPACER)

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
        self.wos_interface.battlefield.clear_scene()

        self.wos_interface.battlefield.update_map(turn_info.map_data)
        self.field_info = self.wos_interface.battlefield.battle_scene.get_field_info()

        self.ships_friendly_items = dict()
        for i in range(0, len(turn_info.self_ship_list)):
            ship_item = self.insert_ship_to_scene(scene, turn_info.self_ship_list[i], ShipInfo.Type.FRIENDLY)
            if ship_item is not None:
                ship_id = ship_item.ship_info.ship_id
                self.ships_friendly_items[ship_id] = ship_item

        self.ships_hostile_items = []
        for i in range(0, len(turn_info.enemy_ship_list)):
            ship_item = self.insert_ship_to_scene(scene, turn_info.enemy_ship_list[i], ShipInfo.Type.HOSTILE)
            if ship_item is not None:
                self.ships_hostile_items.append(ship_item)

        self.ships_other_items = []
        for i in range(0, len(turn_info.other_ship_list)):
            ship_item = self.insert_ship_to_scene(scene, turn_info.other_ship_list[i], ShipInfo.Type.UNKNOWN)
            if ship_item is not None:
                self.ships_other_items.append(ship_item)

        for widget in self.move_action_widgets:
            widget.update_move_ship_combo(self.ships_friendly_items)

        self.insert_annotations_to_scene(self.wos_interface.battlefield.battle_scene.scene())

        self.time_widget.setEnabled(True)
        self.wos_interface.actions.setEnabled(True)

        # Display turn info in log, except for map_data
        turn_info_visual = vars(turn_info)
        turn_info_visual.pop('map_data', None)
        self.wos_interface.log(turn_info_visual, cCommonGame.LogType.DEBUG)

    def submit_button_pressed(self):
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

        self.end_turn()

        self.update_timer.start()

    def update_game_event(self):
        game_status = WosClientInterfaceManager().get_game_status()
        if game_status is not None:
            if self.current_player_turn != game_status.player_turn or self.current_player_round != game_status.game_round:
                self.wos_interface.log(
                    "Round %s: Player %s turn" % (game_status.game_round, game_status.player_turn))
                self.update_turn()

            if self.is_current_turn(game_status):
                self.time_widget.set_time(game_status.time_remain)
            else:
                self.end_turn()

            self.current_player_turn = game_status.player_turn
            self.current_player_round = game_status.game_round

        # Update event again in x seconds time
        self.update_timer.start()

    def update_game_event_parallel(self):
        game_status = WosClientInterfaceManager().get_game_status()
        if game_status is not None and self.current_player_round != game_status.game_round:
            self.wos_interface.log("Round %s started" % game_status.game_round)
            self.update_turn()
            self.current_player_turn = game_status.player_turn
            self.current_player_round = game_status.game_round

        if game_status is not None:
            print(game_status.time_remain)
            self.time_widget.set_time(game_status.time_remain)

        # Update event again in x seconds time
        self.update_timer.start()
