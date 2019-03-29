from client.underwater.issue_waypoints_dialog import WosIssueWaypointsDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setCentralWidget(WosIssueWaypointsDialog(60, 60))
    win.show()
    sys.exit(app.exec_())
