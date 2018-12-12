import sys
from PyQt5 import QtWidgets
from main_window import WosMainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = WosMainWindow()
    mainWin.show()
    sys.exit(app.exec_())
