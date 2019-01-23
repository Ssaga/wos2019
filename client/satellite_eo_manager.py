from PyQt5.QtCore import QObject
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidget
from client.action_widget import WosActionWidget
from client.client_interface_manager import WosClientInterfaceManager
import cCommonGame


class WosSatelliteEoManager(QObject):

    def __init__(self, wos_interface, parent=None):
        QObject.__init__(self, parent)
        self.wos_interface = wos_interface
        self.dialog = None

    def display_pop_up(self):
        if self.dialog is not None:
            self.dialog.deleteLater()
            self.dialog = None

        self.dialog = self.make_pop_up_dialog()
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def make_pop_up_dialog(self):
        dialog = QDialog(self.wos_interface.main_window())
        dialog.setWindowTitle('Please input the 6 parameter')
        dialog.setMinimumWidth(50)
        dialog.accepted.connect(self.submit_command)
        dialog.text_list = []

        layout = QGridLayout(dialog)
        dialog.setLayout(layout)

        dbl_validator = QDoubleValidator()
        for i in range(0, 6):
            layout.addWidget(QLabel("%s:" % i), i, 0)
            line_edit = QLineEdit()
            line_edit.setValidator(dbl_validator)
            line_edit.setText('0.0')
            layout.addWidget(line_edit, i, 1)
            dialog.text_list.append(line_edit)

        submit_button = QToolButton(dialog)
        submit_button.setText("Send")
        submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        submit_button.released.connect(dialog.accept)
        layout.addWidget(submit_button, 6, 0, 1, 2)

        return dialog

    def update_action_widget(self):
        actions_widget = self.wos_interface.actions

        widget = QWidget(actions_widget)
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        eo_button = QToolButton(widget)
        eo_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        eo_button.setText("Send EO Satellite")
        eo_button.released.connect(self.display_pop_up)
        layout.addWidget(eo_button, 0, 0, 1, 3)

        actions_widget.add_widget(widget, WosActionWidget.WidgetType.ACTION_ADDON)

    def start(self):
        cfg = self.wos_interface.cfg
        if cfg is None or not cfg.en_satellite:
            return

        self.wos_interface.log("EO Satellite mode is enabled")

        self.update_action_widget()

    def submit_command(self):
        satcom = cCommonGame.SatcomInfo()
        satcom.a = self.dialog.text_list[0].text()
        satcom.b = self.dialog.text_list[1].text()
        satcom.c = self.dialog.text_list[2].text()
        satcom.d = self.dialog.text_list[3].text()
        satcom.e = self.dialog.text_list[4].text()
        satcom.f = self.dialog.text_list[5].text()
        self.wos_interface.log("Sending EO satellite..")
        self.dialog.deleteLater()
        self.dialog = None
        WosClientInterfaceManager().send_action_move(satcom)
