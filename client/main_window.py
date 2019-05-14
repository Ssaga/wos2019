from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow
from client.action_widget import WosActionWidget
from client.battlefield_widget import WosBattlefieldWidget
from client.client_interface_manager import WosClientInterfaceManager
from client.console_widget import WosConsoleWidget
from client.loading_overlay_widget import LoadingOverlayWidget
from client.game_manager import WosGameManager
from client.wos_interface import WosInterface


class WosMainWindow(QMainWindow):
    make_widgets_ended = pyqtSignal()

    def __init__(self):
        QMainWindow.__init__(self)
        self.wos_interface = WosInterface()

        self.wos_interface.window = self

        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle("World Of Science: Battleship ")
        QCoreApplication.processEvents()

        self.wos_interface.loading_widget = LoadingOverlayWidget(self)

        self.game_manager = None

        self.make_widgets_ended.connect(self.start, Qt.QueuedConnection)

        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.make_widgets)
        self.update_timer.start(600)

    def make_widgets(self):
        self.wos_interface.toggle_overlay(True, 'Initialising...')

        self.wos_interface.battlefield = WosBattlefieldWidget(self.wos_interface, self)
        self.setCentralWidget(self.wos_interface.battlefield)

        self.wos_interface.console = WosConsoleWidget(self)
        self.wos_interface.console.set_log_level(int(self.wos_interface.client_cfg['log_mode']))
        self.addDockWidget(Qt.BottomDockWidgetArea, self.wos_interface.console)

        self.wos_interface.actions = WosActionWidget(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.wos_interface.actions)

        self.make_widgets_ended.emit()

    def start(self):
        self.game_manager = WosGameManager(self.wos_interface, self)
        self.wos_interface.log("Welcome to World of Science.")

    def closeEvent(self, *args, **kwargs):
        if self.game_manager is not None:
            self.game_manager.clean_up()
            self.game_manager.deleteLater()
        self.wos_interface.clean_up()
        WosClientInterfaceManager().disconnect_from_server()

    def __del__(self):
        WosClientInterfaceManager().disconnect_from_server()
