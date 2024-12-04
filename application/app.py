"""
Detection Application Manager

This script provides a GUI application manager using PyQt5, which integrates video detection and a control panel for
device management. The application displays video detection on one screen and the control panel on another if
multiple screens are available.

Classes:
- DetectionApp: A QMainWindow-based class that initializes and manages the application windows.

Functions: - initUI(): Initializes the main user interface, including menu and exit action. - setup_windows(): Sets
up the video detection window and control panel window, positioning them based on available screens.


Author: Kun
Last Modified: 18 Nov 2024
"""
import os
import sys

from PyQt5.QtCore import QCoreApplication, pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QApplication, QMainWindow

_APP_DIR = os.path.dirname(os.path.abspath(__file__))

from .control import Controller
from UI.UI import Ui_MainWindow
from typing import Optional


def get_app() -> Optional[QCoreApplication]:
    """
    Get the current QApplication instance.

    Returns:
        Optional[QCoreApplication]: The current application instance if it exists, otherwise None.
    """
    return QApplication.instance()


class DetectionApp(QMainWindow):
    """
    Main application window for the detection app.

    Attributes:
        init_panel (pyqtSignal): Signal to initialize UI components.
        controller (Controller): Handles the logic and interactions of the app.
    """
    init_panel = pyqtSignal(list)

    def __init__(self, parent=None):
        super(DetectionApp, self).__init__(parent)
        # uic.loadUi('../draft.ui', self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.controller = Controller(self.ui)
        self.handle_signal()

        self.init_panel.emit(self.findChildren(QLineEdit))

    def handle_signal(self):
        self.init_panel.connect(self.controller.init_panel_base)

    def start_detection(self, username, level):
        """
        Start the detection process and display the main window.

        Args:
            username (str): The username of the person starting the detection.
            level (str): The level of detection to initialize.
        """
        if username is not None and level is not None:
            self.controller.username = username
            self.controller.level = level
            self.setGeometry(get_app().screens()[0].geometry())
            self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    detection = DetectionApp()
    detection.show()
    sys.exit(app.exec_())
