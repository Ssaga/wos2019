from client.battle_core_manager import WosBattleCoreManager
from client.phase_manager import WosPhaseManager
from client.satellite_eo_manager import WosSatelliteEoManager
from client.satellite_eo2_manager import WosSatelliteEo2Manager


class WosBattleManager(WosPhaseManager):
    UPDATE_INTERVAL_IN_MS = 1000

    def __init__(self, wos_interface, parent=None):
        WosPhaseManager.__init__(self, wos_interface, parent)
        self.wos_interface = wos_interface
        self.battle_core_manager = WosBattleCoreManager(wos_interface)
        self.features = list()

        self.features.append(self.battle_core_manager)
        self.features.append(WosSatelliteEoManager(wos_interface, self.battle_core_manager))
        self.features.append(WosSatelliteEo2Manager(wos_interface, self.battle_core_manager))

    def start(self):
        for feature in self.features:
            feature.start()
