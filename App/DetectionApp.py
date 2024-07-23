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
from Widget.LogInWindow import LoginWindow
from Widget.VideoWindow import VideoWindow
from Widget.ControlPanel import ControlPanel
from Widget.MenuBar import MenuBar
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QRect
import sys


def applicationSupportsSecureRestorableState_():
    return True


class DetectionApp(QMainWindow):
    def __init__(self, parent=None):
        super(DetectionApp, self).__init__(parent)
        self.video_window = None
        self.control_panel = None
        self.login = LoginWindow()
        self.username = ''
        self.user_level = -1
        self.login.accepted.connect(self.setup_windows)
        self.initUI()
        # self.login.show()

    def initUI(self):
        self.setWindowTitle('Application Manager')
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.login.show()
        self.hide()

    def setup_windows(self, username, user_level):
        self.username, self.user_level = username, user_level
        print(username, user_level)
        screens = app.screens()

        self.video_window = VideoWindow(self)
        self.control_panel = ControlPanel(self)

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
        # self.hide()
        self.video_window.show()
        self.control_panel.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    detection = DetectionApp()
    # detection.login.show()
    sys.exit(app.exec_())
