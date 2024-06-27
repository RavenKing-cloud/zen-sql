# main.py

import sys
from PyQt5.QtWidgets import QApplication
from frontend.mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())