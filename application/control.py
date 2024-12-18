"""
Detection Application Manager

This script provides a GUI application manager using PyQt5, which integrates video detection and a control panel for
device management. The application displays video detection on one screen and the control panel on another if
multiple screens are available.

Classes:
- Controller: Manages application logic, including initialization and signal handling.

Functions:
- get_app(): Retrieves the current QApplication instance.
- init_models(): Loads machine learning models for detection tasks.
- check_dataset(): Ensures the dataset directory and file structure exist.

Author: Kun
Last Modified: 18 Nov 2024
"""
import os

# Define the root directory for the application
_APP_DIR = os.path.dirname(os.path.abspath(__file__))

from widgets.video_window import VideoBase
from widgets.panel import PanelBase
from widgets.menubar import BarBase
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QCoreApplication, QObject, pyqtSlot
from UI.UI import Ui_MainWindow
import sys
from ultralytics import YOLO
from typing import Optional
import csv


def get_app() -> Optional[QCoreApplication]:
    """
    Get the current QApplication instance.

    Returns:
        Optional[QCoreApplication]: The current application instance if it exists, otherwise None.
    """
    return QApplication.instance()


def init_models():
    """
    Initialize and load detection models from specified paths.

    Returns:
        dict: A dictionary of YOLO models mapped to their respective task names.
    """
    model_path = os.path.join(_APP_DIR, '../Models')

    logo_model_path = os.path.join(model_path, 'logo.pt')
    # lot_model_path = os.path.join(model_path, 'lot.pt')
    top_bottom_model_path = os.path.join(model_path, 'top_bottom.pt')
    keyboard_model_path = os.path.join(model_path, 'keyboard.pt')
    screen_model_path = os.path.join(model_path, 'screen.pt')
    # barcode_model_path = os.path.join(model_path, 'barcode.pt')
    laptop_model_path = os.path.join(model_path, 'laptop.pt')
    serial_region_model_path = os.path.join(model_path, 'region.pt')
    serial_model_path = os.path.join(model_path, 'serial.pt')
    lot_asset_barcode_path = os.path.join(model_path, 'lot_asset_barcode.pt')

    defects_model = YOLO(top_bottom_model_path)
    logo_model = YOLO(logo_model_path)
    # lot_model = YOLO(lot_model_path)
    serial_region_model = YOLO(serial_region_model_path)
    serial_model = YOLO(serial_model_path)
    laptop_model = YOLO(laptop_model_path)
    # barcode_model = YOLO(barcode_model_path)
    keyboard_model = YOLO(keyboard_model_path)
    lot_asset_barcode_model = YOLO(lot_asset_barcode_path)

    # Check if screen model exists, set None otherwise
    if os.path.exists(screen_model_path):
        screen_model = YOLO(screen_model_path)
    else:
        screen_model = None

    return {
        'top_bottom': defects_model,
        'logo': logo_model,
        'serial_region': serial_region_model,
        'serial': serial_model,
        'laptop': laptop_model,
        'keyboard': keyboard_model,
        'screen': screen_model,
        'lot_asset_barcode': lot_asset_barcode_model
    }

def check_dataset():
    """
    Ensure that the dataset directory and CSV file exist. Create them if they do not.
    """
    root_path = os.path.abspath(os.path.join(_APP_DIR, '..'))
    dataset_dir_path = os.path.join(root_path, 'dataset')
    if not os.path.exists(dataset_dir_path):
        os.makedirs(dataset_dir_path)
        dataset_file = os.path.join(dataset_dir_path, 'dataset.csv')
        fieldnames = ['model', 'serial number', 'lot number', 'grade', 'stain', 'scratch']
        # Create and initialize the CSV file with headers
        with open(dataset_file, 'a', newline='', encoding='utf-8') as dataset:
            writer = csv.DictWriter(dataset, fieldnames=fieldnames)
            writer.writeheader()


class Controller(QObject):
    """
    Main controller for the detection application.

    Attributes:
        ui (Ui_MainWindow): The UI instance for the application.
        username (str): The username of the logged-in user.
        level (int): Access level of the user.
        thread_labels (list): List of video thread labels for video feed.
        video_buttons (dict): Buttons related to video detection.
        video_widget (VideoBase): Video detection widget instance.
        input_lines (dict): Dictionary of input lines in the panel.
        panel_buttons (dict): Buttons related to the control panel.
        panel_widget (PanelBase): Panel widget instance.
        actionDict (dict): Dictionary of menu actions.
        menuBar (BarBase): Custom menu bar instance.
    """
    def __init__(self, UI):
        super().__init__()
        self.ui = UI
        self.username = ''
        self.level = -1
        self.thread_labels = []
        self.video_buttons = {}
        self.video_widget = None

        self.input_lines = {}
        self.panel_buttons = {}
        self.panel_widget = None
        
        self.actionDict = {}
        self.menuBar = None
        self.init_menu_bar()
        check_dataset()

        self.models = init_models()
        self.init_video_base()

        self.handle_signal()

    def handle_signal(self):
        pass

    def init_menu_bar(self):
        actionOpenFile = getattr(self.ui, 'actionOpenFile')
        # if actionOpenFile.parent() is None:
        #     actionOpenFile.setParent(self.ui.main_window)
        self.actionDict['openFile'] = actionOpenFile

        actionExitApp = getattr(self.ui, 'actionExitApp')
        # if actionExitApp.parent() is None:
        #     actionExitApp.setParent(self.ui.main_window)
        self.actionDict['exitApp'] = actionExitApp

        actionOpenDatabase = getattr(self.ui, 'actionOpenDatabase')
        self.actionDict['openDatabase'] = actionOpenDatabase

        actionExportData = getattr(self.ui, 'actionExportData')
        self.actionDict['exportData'] = actionExportData

        actionProfile = getattr(self.ui, 'actionProfile')
        self.actionDict['profile'] = actionProfile

        actionSignout = getattr(self.ui, 'actionSignout')
        self.actionDict['signout'] = actionSignout

        actionDocuments = getattr(self.ui, 'actionDocuments')
        self.actionDict['documents'] = actionDocuments

        actionInstructions = getattr(self.ui, 'actionInstructions')
        self.actionDict['instructions'] = actionInstructions

        self.menuBar = BarBase(self.actionDict)

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
        """
        Initialize the control panel widget.

        Args:
            input_lines (list): List of input fields in the control panel.
        """
        for input_line in input_lines:
            name = input_line.objectName()
            # print(f"Input name: {name}")
            self.input_lines[name] = input_line

        # Collect control panel buttons from the UI
        save_button = getattr(self.ui, 'save_button')
        self.panel_buttons['save_button'] = save_button

        clear_button = getattr(self.ui, 'clear_button')
        self.panel_buttons['clear_button'] = clear_button

        self.panel_widget = PanelBase(self.input_lines, self.panel_buttons)
        # Connect detected features from video widget to the panel
        self.video_widget.laptop_info.connect(self.panel_widget.set_detected_features)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    controller = Controller(ui)
    controller.init_panel_base()
    # sys.exit(app.exec_())
