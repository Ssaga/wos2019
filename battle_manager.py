from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client_interface_manager import WosClientInterfaceManager
from phase_manager import WosPhaseManager


class WosBattleManager(WosPhaseManager):
    deployment_ended = pyqtSignal()

    def __init__(self, wos_interface, parent=None):
        WosPhaseManager.__init__(self, wos_interface, parent)

    def start(self):
        self.wos_interface.log("<b>Battle phase</b>.")

        scene = self.wos_interface.battlefield.battle_scene.scene()
        self.wos_interface.battlefield.generate_scene(120, 120)
        field_info = self.wos_interface.battlefield.battle_scene.get_field_info()

        self.update_action_widget()

    def update_action_widget(self):
        actions_widget = self.wos_interface.actions

        widget = QWidget(actions_widget)
        layout = QGridLayout(widget)
        widget.setLayout(layout)

        move_1_combo = QComboBox(widget)
        layout.addWidget(QLabel('Move 1:'), 0, 0)
        layout.addWidget(move_1_combo, 0, 1)

        move_2_combo = QComboBox(widget)
        layout.addWidget(QLabel('Move 2:'), 1, 0)
        layout.addWidget(move_2_combo, 1, 1)

        layout.addWidget(QLabel('Bomb:'), 2, 0)
        attack_x_combo = QComboBox(widget)
        layout.addWidget(attack_x_combo, 2, 1)
        attack_y_combo = QComboBox(widget)
        layout.addWidget(attack_y_combo, 2, 2)

        submit_button = QToolButton(widget)
        submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        submit_button.setText("End Turn")
        # submit_button.released.connect(self.button_pressed)
        layout.addWidget(submit_button, 3, 0, 1, 3)

        actions_widget.append_widget(widget)
