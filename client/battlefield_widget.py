from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QWidget
from client.battlefield_view import WosBattleFieldView
from client.ship_info import ShipInfo


class WosBattlefieldWidget(QWidget):
    show_terrain_context_menu = pyqtSignal(QContextMenuEvent, int, int, int)
    show_battleship_context_menu = pyqtSignal(QContextMenuEvent, ShipInfo, int, int)

    def __init__(self, wos_interface, parent=None):
        QWidget.__init__(self, parent)

        layout = QGridLayout(self)
        self.setLayout(layout)

        self.battle_scene = WosBattleFieldView(wos_interface, QPoint(60, 60), self)
        self.battle_scene.show_terrain_context_menu.connect(self.show_terrain_context_menu)
        self.battle_scene.show_battleship_context_menu.connect(self.show_battleship_context_menu)
        layout.addWidget(self.battle_scene, 0, 0)

    def clear_scene(self):
        self.battle_scene.clear()

    def generate_scene(self, width, height):
        self.battle_scene.set_dimension(width, height)

    def update_map(self, map_data):
        self.battle_scene.update_map(map_data)
