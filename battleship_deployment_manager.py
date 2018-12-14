from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from battleship_item import WosBattleShipItem
from client_interface_manager import WosClientInterfaceManager
from phase_manager import WosPhaseManager


class WosBattleShipDeploymentManager(WosPhaseManager):
    deployment_ended = pyqtSignal()

    def __init__(self, wos_interface, parent=None):
        WosPhaseManager.__init__(self, wos_interface, parent)
        self.ships_items = []
        self.tools = None

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
        if WosClientInterfaceManager().send_deployment(ships):
            self.wos_interface.log("Server acknowledged")
        else:
            self.wos_interface.log("Server declined")
        # todo; Don't end if server did not acknowledged
        self.end()

    def start(self):
        self.wos_interface.log("<b>Deployment phase</b>.")
        self.wos_interface.log("Please assign the ships to a desired location in the map. Click and drag the ships to "
                               "reposition with left mouse button, rotate the ships with right mouse button.")

        scene = self.wos_interface.battlefield.battle_scene.scene()
        self.wos_interface.battlefield.generate_scene(60, 60)
        field_info = self.wos_interface.battlefield.battle_scene.get_field_info()

        # Read config file for squad list, stub for now
        self.ships_items = [WosBattleShipItem(field_info, 2), WosBattleShipItem(field_info, 2),
                            WosBattleShipItem(field_info, 3), WosBattleShipItem(field_info, 3),
                            WosBattleShipItem(field_info, 4), WosBattleShipItem(field_info, 4),
                            WosBattleShipItem(field_info, 5), WosBattleShipItem(field_info, 5)]

        for i in range(0, len(self.ships_items)):
            scene.addItem(self.ships_items[i])
            self.ships_items[i].set_grid_position(i, 0)

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
