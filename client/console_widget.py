from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QWidget
import cCommonGame
import datetime


class WosConsoleWidget(QDockWidget):
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent)

        self.mode = cCommonGame.LogType.ALL

        self.setWindowTitle('Console')
        self.setMinimumWidth(500)

        widget = QWidget(self)
        self.setWidget(widget)
        layout = QGridLayout(widget)

        self.console = QTextBrowser(self)
        self.console.setReadOnly(True)
        self.console.setOpenLinks(False)
        self.console.anchorClicked.connect(self.url_clicked)
        layout.addWidget(self.console, 0, 0)

    def log_simple(self, text, type=cCommonGame.LogType.GAME):
        now = datetime.datetime.now()
        self.log(now.strftime("%d-%m-%Y %H:%M:%S"), text, type)

    def log(self, date_and_time_string, text, type=cCommonGame.LogType.GAME):
        if self.mode & type:
            if type & cCommonGame.LogType.DEBUG:
                line = "{}: <font color='brown'><i>{}</i></font><br>".format(date_and_time_string, text)
            else:
                line = "{}: {}<br>".format(date_and_time_string, text)
            self.console.insertHtml(line)
            self.console.ensureCursorVisible()

    def url_clicked(self, link):
        print (link)
        QDesktopServices.openUrl(link)

    def set_log_level(self, mode):
        self.mode = mode
