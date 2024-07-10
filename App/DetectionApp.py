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

from Widget.VideoWindow import *
from Widget.ControlPanel import *
from PyQt5.QtWidgets import QApplication, QAction, QMainWindow
from PyQt5.QtCore import QRect
import sys


class DetectionApp(QMainWindow):
    def __init__(self, master):
        super().__init__()
        self.video_window = None
        self.control_panel = None
        self.app = master
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Application Manager')
        self.hide()
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.app.quit)
        file_menu.addAction(exit_action)
        self.setup_windows()

    def setup_windows(self):
        screens = self.app.screens()
        # print(len(screens))

        self.video_window = VideoWindow()
        self.control_panel = ControlPanel()

        if len(screens) > 1:
            self.video_window.setGeometry(screens[0].geometry())
            self.control_panel.setGeometry(screens[1].geometry())
        else:
            video_geometry = QRect(100, 100, 800, 600)
            control_geometry = QRect(900, 100, 300, 200)
            self.video_window.setGeometry(video_geometry)
            self.control_panel.setGeometry(control_geometry)

        # video_geometry = QRect(100, 100, 800, 600)
        # control_geometry = QRect(900, 100, 300, 200)
        # self.video_window.setGeometry(video_geometry)
        # self.control_panel.setGeometry(control_geometry)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    detection = DetectionApp(app)
    sys.exit(app.exec_())
