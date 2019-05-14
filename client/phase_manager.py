from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal


class WosPhaseManager(QObject):
    phase_ended = pyqtSignal()

    def __init__(self, wos_interface, parent=None):
        QObject.__init__(self, parent)
        self.wos_interface = wos_interface

    def clean_up(self):
        pass

    def start(self):
        raise NotImplementedError()

    def end(self):
        self.phase_ended.emit()
