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

from Widgets.VideoBase import *
from Widgets.ControlPanel import PanelBase
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QLineEdit
from PyQt5.QtCore import QRect, QCoreApplication, QObject, pyqtSlot
from IO.ImageSaver import *
import easyocr
from UI import *
import sys
from ultralytics import YOLO


def get_app() -> QCoreApplication | None:
    return QApplication.instance()


def init_models():
    model_path = os.path.join(_APP_DIR, '../Models')
    logo_model_path = os.path.join(model_path, 'logo.pt')
    ocr_model_path = os.path.join(model_path, 'ocr.pt')
    detect_model_path = os.path.join(model_path, 'detect.pt')
    detect_model = YOLO(detect_model_path)
    logo_model = YOLO(logo_model_path)
    ocr_model = YOLO(ocr_model_path)
    reader = easyocr.Reader(['en'], gpu=False)
    return {'detect': detect_model, 'logo': logo_model, 'ocr': ocr_model, 'reader': reader}


class Controller(QObject):

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.username = ''
        self.level = -1
        self.thread_labels = []
        self.video_buttons = {}
        self.video_widget = None

        self.input_lines = {}
        self.panel_buttons = {}
        self.panel_widget = None

        self.models = init_models()
        self.init_video_base()

        self.handle_signal()

    def handle_signal(self):
        pass

    def init_video_base(self):
        for i in range(6):
            video_thread = getattr(self.ui, f'video_thread_{i+1}')
            self.thread_labels.append(video_thread)

        detect_button = getattr(self.ui, 'start_detection_button')
        self.video_buttons['detect_button'] = detect_button

        capture_button = getattr(self.ui, 'capture_images_button')
        self.video_buttons['capture_button'] = capture_button

        stop_button = getattr(self.ui, 'stop_detection_button')
        self.video_buttons['stop_button'] = stop_button

        self.video_widget = VideoBase(thread_labels=self.thread_labels,
                                      buttons=self.video_buttons, models=self.models)

    @pyqtSlot(list)
    def init_panel_base(self, input_lines):
        for input_line in input_lines:
            name = input_line.objectName()
            # print(f'Input name: {name}')
            self.input_lines[name] = input_line
        save_button = getattr(self.ui, 'save_button')
        self.panel_buttons['save_button'] = save_button

        clear_button = getattr(self.ui, 'clear_button')
        self.panel_buttons['clear_button'] = clear_button

        self.panel_widget = PanelBase(self.input_lines, self.panel_buttons)
        self.video_widget.laptop_info.connect(self.panel_widget.set_laptop_info)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainwindow)
    controller = Controller(ui)
    controller.init_panel_base()
    # sys.exit(app.exec_())
