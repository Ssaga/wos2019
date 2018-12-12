from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from action_widget import WosActionWidget
from battlefield_widget import WosBattlefieldWidget
from console_widget import WosConsoleWidget
from wos_interface import WosInterface
from battleship_deployment_manager import WosBattleShipDeploymentManager
from client_interface import WosClicentInterface

class WosMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.interface = WosInterface()

        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle("World Of Science: Battleship ")

        WosClicentInterface.connect_to_server()

        self.interface.battlefield = WosBattlefieldWidget(self)
        self.setCentralWidget(self.interface.battlefield)

        self.interface.console = WosConsoleWidget(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.interface.console)

        self.interface.actions = WosActionWidget(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.interface.actions)

        self.deployment_manager = WosBattleShipDeploymentManager(self.interface, self)

    def closeEvent(self, *args, **kwargs):
        WosClicentInterface.disconnect_from_server()



