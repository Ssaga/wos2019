from client.phase_manager import WosPhaseManager


class WosFinalManager(WosPhaseManager):

    def __init__(self, wos_interface, parent=None):
        WosPhaseManager.__init__(self, wos_interface, parent)

    def start(self):
        self.wos_interface.log("<b>Game Ended</b>.")
