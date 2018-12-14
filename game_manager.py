from enum import IntEnum
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from battle_manager import WosBattleManager
from battleship_deployment_manager import WosBattleShipDeploymentManager


class WosGameManager(QObject):
    state_changed = pyqtSignal(int, int)

    class GameState(IntEnum):
        INIT = 0
        DEPLOYMENT = 1
        BATTLE = 2
        END = 3

    def __init__(self, wos_interface, parent=None):
        QObject.__init__(self, parent)
        self.wos_interface = wos_interface
        self.state = WosGameManager.GameState.INIT
        self.state_managers = dict()
        self.state_managers[WosGameManager.GameState.INIT] = None
        self.state_managers[WosGameManager.GameState.DEPLOYMENT] = WosBattleShipDeploymentManager(self.wos_interface,
                                                                                                  self)
        self.state_managers[WosGameManager.GameState.BATTLE] = WosBattleManager(self.wos_interface, self)
        self.state_managers[WosGameManager.GameState.END] = None

        self.state_changed.connect(self.change_state)

        self.next_state()

    def change_state(self, old_state, new_state):
        self.state = new_state
        state_manager = self.state_managers[self.state]
        state_manager.start()
        state_manager.phase_ended.connect(self.next_state)

    def next_state(self):
         self.state_changed.emit(self.state, self.state + 1)
