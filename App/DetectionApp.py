from Widget.VideoWindow import *
from Widget.ControlPanel import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect
import sys


class ApplicationManager:
    def __init__(self):
        self.video_window = None
        self.control_panel = None
        self.app = QApplication(sys.argv)
        self.setup_windows()

    def setup_windows(self):
        screens = self.app.screens()

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

    def run(self):
        self.video_window.show()
        self.control_panel.show()
        sys.exit(self.app.exec_())

