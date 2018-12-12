from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from battleship_item import WosBattleShipItem
from client_interface import WosClicentInterface


class WosBattleShipDeploymentManager(QObject):
    def __init__(self, wos_interface, parent=None):
        QObject.__init__(self, parent)

        self.wos_interface = wos_interface

        self.wos_interface.log("<b>Deployment phase</b>.")
        self.wos_interface.log("Please assign the ships to a desired location in the map. Click and drag the ships to "
                               "reposition with left mouse button, rotate the ships with right mouse button.")

        scene = self.wos_interface.battlefield.battle_scene.scene()
        field_info = self.wos_interface.battlefield.battle_scene.get_field_info()

        # Read config file for squad list, stub for now
        self.ships = [WosBattleShipItem(field_info, 2), WosBattleShipItem(field_info, 2),
                      WosBattleShipItem(field_info, 3), WosBattleShipItem(field_info, 3),
                      WosBattleShipItem(field_info, 4), WosBattleShipItem(field_info, 4),
                      WosBattleShipItem(field_info, 5), WosBattleShipItem(field_info, 5)]

        for i in range(0, len(self.ships)):
            scene.addItem(self.ships[i])
            self.ships[i].set_grid_position(i, 0)

        self.update_action_widget()

    def update_action_widget(self):
        actions_widget = self.wos_interface.actions

        widget = QWidget(actions_widget)
        layout = QVBoxLayout(widget)
        widget.setLayout(layout)

        deployment_button = QToolButton(widget)
        deployment_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        deployment_button.setText("Confirm Deployment")
        deployment_button.released.connect(self.deployment_button_pressed)
        layout.addWidget(deployment_button)

        actions_widget.append_widget(widget)

    def deployment_button_pressed(self):
        self.send_deployment()
        # reply = QMessageBox.question(self.parent(), 'Confirm', "Confirm the deployment?",
        #                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # if reply == QMessageBox.Yes:
        #     self.send_deployment()

    def send_deployment(self):
        WosClicentInterface.send_deployment()

    def end(self):
        scene = self.wos_interface.battlefield.battle_scene.scene()
        for i in range(0, len(self.ships)):
            scene.removeItem(self.ships[i])
