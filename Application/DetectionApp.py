"""
Detection Application Manager

This script provides a GUI application manager using PyQt5, which integrates video detection and a control panel for device management.
The application displays video detection on one screen and the control panel on another if multiple screens are available.

Classes:
- DetectionApp: A QMainWindow-based class that initializes and manages the application windows.

Functions:
- initUI(): Initializes the main user interface, including menu and exit action.
- setup_windows(): Sets up the video detection window and control panel window, positioning them based on available screens.


Author: Kun
Last Modified: 10 Jul 2024
"""
import os
_APP_DIR = os.path.dirname(os.path.abspath(__file__))

from App.Controller import *
from typing import Optional


def get_app() -> Optional[QCoreApplication]:
    return QApplication.instance()


class DetectionApp(QMainWindow):
    init_panel = pyqtSignal(list)

    def __init__(self, parent=None):
        super(DetectionApp, self).__init__(parent)
        # uic.loadUi('../draft.ui', self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setGeometry(get_app().screens()[0].geometry())
        self.controller = Controller(self.ui)
        self.handle_signel()

        self.init_panel.emit(self.findChildren(QLineEdit))

    def handle_signel(self):
        self.init_panel.connect(self.controller.init_panel_base)

    def start_detection(self, username, level):
        if username is not None and level is not None:
            self.controller.username = username
            self.controller.level = level
            self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    detection = DetectionApp()
    detection.show()
    sys.exit(app.exec_())
