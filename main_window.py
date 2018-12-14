from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from action_widget import WosActionWidget
from battle_manager import WosBattleManager
from battlefield_widget import WosBattlefieldWidget
from console_widget import WosConsoleWidget
from client_interface_manager import WosClientInterfaceManager
from game_manager import WosGameManager
from wos_interface import WosInterface


class WosMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.interface = WosInterface()

        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle("World Of Science: Battleship ")

        WosClientInterfaceManager().connect_to_server()

        self.interface.battlefield = WosBattlefieldWidget(self)
        self.setCentralWidget(self.interface.battlefield)

        self.interface.console = WosConsoleWidget(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.interface.console)

        self.interface.actions = WosActionWidget(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.interface.actions)

        self.game_manager = WosGameManager(self.interface, self)

    def closeEvent(self, *args, **kwargs):
        WosClientInterfaceManager().disconnect_from_server()
