from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client.battleship_item import WosBattleShipItem
from client.client_interface_manager import WosClientInterfaceManager
from client.phase_manager import WosPhaseManager
import cCommonGame


class WosBattleManager(WosPhaseManager):
    UPDATE_INTERVAL_IN_MS = 1000

    deployment_ended = pyqtSignal()

    def __init__(self, wos_interface, parent=None):
        WosPhaseManager.__init__(self, wos_interface, parent)
        self.current_player_turn = 0
        self.current_player_round = 0
        self.field_info = None
        # todo: Read from config file or get from server
        self.num_move_actions = 2
        self.num_fire_actions = 1
        self.ships_items = []
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_game_event)

    def is_current_turn(self, game_status):
        return game_status.player_turn == self.wos_interface.player_info.player_id

    def start(self):
        self.wos_interface.log("<b>Battle phase</b>.")
        self.update_action_widget()
        self.update_timer.start(self.UPDATE_INTERVAL_IN_MS)

    def update_action_widget(self):
        actions_widget = self.wos_interface.actions

        widget = QWidget(actions_widget)
        layout = QGridLayout(widget)
        widget.setLayout(layout)

        form_row = 0
        for i in range(1, self.num_move_actions + 1):
            layout.addWidget(QLabel("Move %s:" % i), form_row, 0)
            move_ship_combo = QComboBox(widget)
            move_ship_combo.setObjectName("ship_%s_combo" % i)
            layout.addWidget(move_ship_combo, form_row, 1)
            move_action_combo = QComboBox(widget)
            move_action_combo.setObjectName("action_%s_combo" % i)
            move_action_combo.addItem('Forward', cCommonGame.Action.FWD)
            move_action_combo.addItem('Turn clockwise', cCommonGame.Action.CW)
            move_action_combo.addItem('Turn anti-clockwise', cCommonGame.Action.CCW)
            move_action_combo.addItem('Skip', cCommonGame.Action.NOP)
            layout.addWidget(move_action_combo, form_row, 2)
            form_row += 1

        for i in range(1, self.num_fire_actions + 1):
            layout.addWidget(QLabel("Bomb %s:" % i), form_row, 0)
            attack_x_combo = QComboBox(widget)
            attack_x_combo.setObjectName("attack_x_%s_combo" % i)
            # todo: Read from config
            for j in range(0, 120):
                # for j in range(0, self.field_info.dimension.x()):
                attack_x_combo.addItem(str(j), j)
            layout.addWidget(attack_x_combo, form_row, 1)
            attack_y_combo = QComboBox(widget)
            attack_y_combo.setObjectName("attack_y_%s_combo" % i)
            # todo: Read from config
            for j in range(0, 120):
                # for j in range(0, self.field_info.dimension.x()):
                attack_y_combo.addItem(str(j), j)
            layout.addWidget(attack_y_combo, form_row, 2)
            form_row += 1

        submit_button = QToolButton(widget)
        submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        submit_button.setText("End Turn")
        submit_button.released.connect(self.submit_button_pressed)
        layout.addWidget(submit_button, form_row, 0, 1, 3)

        actions_widget.append_widget(widget)

        actions_widget.setEnabled(False)

    def update_turn(self):
        turn_info = WosClientInterfaceManager().get_turn_info()
        # Handle case where update_turn was wrongly called
        if not turn_info or not turn_info.ack:
            self.update_timer.start()
            return

        scene = self.wos_interface.battlefield.battle_scene.scene()
        self.wos_interface.battlefield.update_map(turn_info.map_data)
        self.field_info = self.wos_interface.battlefield.battle_scene.get_field_info()

        self.ships_items = list()
        for i in range(0, len(turn_info.ship_list)):
            ship = turn_info.ship_list[i]
            ship_item = WosBattleShipItem(self.field_info, ship.ship_id, ship.size)
            ship_item.set_grid_position(ship.position.x, ship.position.y)
            ship_item.set_heading(ship.heading)
            self.ships_items.append(ship_item)
            scene.addItem(ship_item)

        actions_widget = self.wos_interface.actions
        for i in range(1, self.num_move_actions + 1):
            combo = actions_widget.findChildren(QComboBox, "ship_%s_combo" % i)
            if len(combo) > 0:
                combo = combo[0]
                combo.clear()
                for ship_item in self.ships_items:
                    combo.addItem(str(ship_item.ship_info.ship_id), ship_item.ship_info.ship_id)

        self.wos_interface.actions.setEnabled(True)

    def submit_button_pressed(self):
        actions_widget = self.wos_interface.actions
        actions_widget.setEnabled(False)

        # Collate move action(s)
        move_list = list()
        for i in range(1, self.num_move_actions + 1):
            combo = actions_widget.findChildren(QComboBox, "ship_%s_combo" % i)
            ship_id = 0
            if len(combo) > 0:
                ship_id = combo[0].currentData()
            combo = actions_widget.findChildren(QComboBox, "action_%s_combo" % i)
            action = cCommonGame.Action.NOP
            if len(combo) > 0:
                action = combo[0].currentData()
            move_list.append(cCommonGame.ShipMovementInfo(ship_id, action))

        # Collate fire action(s)
        fire_list = list()
        for i in range(1, self.num_fire_actions + 1):
            x = 1
            combo = actions_widget.findChildren(QComboBox, "attack_x_%s_combo" % i)
            if len(combo) > 0:
                x = combo[0].currentData()
            y = 1
            combo = actions_widget.findChildren(QComboBox, "attack_y_%s_combo" % i)
            if len(combo) > 0:
                y = combo[0].currentData()
            fire_list.append(cCommonGame.FireInfo(cCommonGame.Position(x, y)))

        self.wos_interface.log("Sending commands to server..")

        # Consider doing validations
        WosClientInterfaceManager().send_action_move(move_list)
        WosClientInterfaceManager().send_action_attack(fire_list)

        self.wos_interface.log("Sent")

        self.update_timer.start()

    def update_game_event(self):
        game_status = WosClientInterfaceManager().get_game_status()
        print(vars(game_status))
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
