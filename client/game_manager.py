from enum import IntEnum
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from client.battle_manager import WosBattleManager
from client.battleship_deployment_manager import WosBattleShipDeploymentManager
from client.creation_manager import WosCreationManager
from client.final_manager import WosFinalManager


class WosGameManager(QObject):
    state_changed = pyqtSignal(int, int)

    class GameState(IntEnum):
        INIT = 0
        CREATION = 1
        DEPLOYMENT = 2
        BATTLE = 3
        END = 4

    def __init__(self, wos_interface, parent=None):
        QObject.__init__(self, parent)
        self.wos_interface = wos_interface
        self.state = WosGameManager.GameState.INIT
        self.state_managers = dict()
        self.state_managers[WosGameManager.GameState.INIT] = None
        self.state_managers[WosGameManager.GameState.CREATION] = WosCreationManager(self.wos_interface, self)
        self.state_managers[WosGameManager.GameState.DEPLOYMENT] = WosBattleShipDeploymentManager(self.wos_interface,
                                                                                                  self)
        self.state_managers[WosGameManager.GameState.BATTLE] = WosBattleManager(self.wos_interface, self)
        self.state_managers[WosGameManager.GameState.END] = WosFinalManager(self.wos_interface, self)

        self.state_changed.connect(self.change_state)

        # Add delay to starting game for allowing GUI to be properly set up first
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.next_state)
        timer.start(100)

    def clean_up(self):
        for state in self.state_managers.values():
            if state is not None:
                state.clean_up()
        self.state_managers.clear()

    def change_state(self, old_state, new_state):
        self.state = new_state
        state_manager = self.state_managers[self.state]
        state_manager.phase_ended.connect(self.next_state)
        self.wos_interface.toggle_overlay(False)
        state_manager.start()

    def next_state(self):
        self.state_changed.emit(self.state, self.state + 1)
