from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QWidget
import datetime


class WosConsoleWidget(QDockWidget):
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent)

        self.setWindowTitle('Console')
        self.setMinimumWidth(500)

        widget = QWidget(self)
        self.setWidget(widget)

        layout = QGridLayout(self)
        widget.setLayout(layout)

        self.console = QTextEdit('', self)
        layout.addWidget(self.console, 0, 0)

        self.log_simple("Welcome to World of Science.")
        self.log_simple("You have 30mins to solve the puzzles before the bomb explodes, all the best.")

    def log_simple(self, text):
        now = datetime.datetime.now()
        self.log(now.strftime("%d-%m-%Y %H:%M:%S"), text)

    def log(self, date_and_time_string, text):
        line = "{}: {}<br>".format(date_and_time_string, text)
        self.console.insertHtml(line)
