from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QWidget
from client.battlefield_view import WosBattleFieldView


class WosBattlefieldWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        layout = QGridLayout(self)
        self.setLayout(layout)

        self.battle_scene = WosBattleFieldView(QPoint(60, 60), self)
        layout.addWidget(self.battle_scene, 0, 0)

    def clear_scene(self):
        self.battle_scene.clear()

    def generate_scene(self, width, height):
        self.battle_scene.set_dimension(width, height)

    def update_map(self, map_data):
        self.battle_scene.update_map(map_data)
