import sys

from PyQt5.QtWidgets import QApplication

from IO.export import ExportFile

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = ExportFile()
    mainWindow.show()
    sys.exit(app.exec_())
