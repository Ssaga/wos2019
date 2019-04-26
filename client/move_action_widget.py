from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

import cCommonGame


class WosMoveActionWidget(QWidget):
    combo_updated = pyqtSignal()

    def __init__(self, index, parent=None):
        QWidget.__init__(self, parent)
        self.index = index

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Move %s:" % index, self), 0, 0)
        self.move_ship_combo = QComboBox(self)
        self.move_ship_combo.currentTextChanged.connect(self.combo_updated)
        self.layout.addWidget(self.move_ship_combo, 0, 1)
        self.move_action_combo = QComboBox(self)
        self.move_action_combo.currentTextChanged.connect(self.combo_updated)
        self.move_action_combo.addItem('Forward', cCommonGame.Action.FWD)
        self.move_action_combo.addItem('Turn clockwise', cCommonGame.Action.CW)
        self.move_action_combo.addItem('Turn anti-clockwise', cCommonGame.Action.CCW)
        self.move_action_combo.addItem('Skip', cCommonGame.Action.NOP)
        self.layout.addWidget(self.move_action_combo, 0, 2)

    def get_index(self):
        return self.index

    def get_move_info(self):
        return self.move_ship_combo.currentData(), self.move_action_combo.currentData()

    def set_ship_actions(self, ship_id, action):
        self.move_ship_combo.setCurrentText(str(ship_id))
        if action == cCommonGame.Action.FWD:
            self.move_action_combo.setCurrentText('Forward')
        elif action == cCommonGame.Action.CW:
            self.move_action_combo.setCurrentText('Turn clockwise')
        elif action == cCommonGame.Action.CCW:
            self.move_action_combo.setCurrentText('Turn anti-clockwise')
        else:
            self.move_action_combo.setCurrentText('Skip')

    def update_move_ship_combo(self, ships):
        self.move_ship_combo.blockSignals(True)
        # Preserve last command
        old_text = self.move_ship_combo.currentText()
        self.move_ship_combo.clear()
        for ship_id, ship in ships.items():
            if not ship.ship_info.is_sunken:
                self.move_ship_combo.addItem(str(ship_id), ship_id)
        if not old_text:
            # Default index
            self.move_ship_combo.setCurrentIndex(self.index - 1)
        else:
            self.move_ship_combo.setCurrentText(old_text)
        self.move_ship_combo.blockSignals(False)
