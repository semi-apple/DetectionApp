import os
import pytest
import csv

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from application.control import Controller, init_models, check_dataset
from UI.UI import Ui_MainWindow
from unittest.mock import MagicMock


@pytest.fixture
def main_window(qtbot):
    window = QMainWindow()
    qtbot.addWidget(window)
    return window


@pytest.fixture(scope='module')
def app():
    qt_app = QApplication.instance()
    return qt_app


@pytest.fixture
def controller(main_window):
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    return Controller(ui)


def test_init_models():
    models = init_models()
    required_models = ["top_bottom", "logo", "lot", "serial_region", "serial", "laptop", "barcode", "keyboard"]
    for model in required_models:
        assert model in models, f"{model} should be initialized."


def test_check_dataset(tmp_path, monkeypatch):
    mock_root = tmp_path / 'mock_root'
    monkeypatch.setattr('application.control._APP_DIR', str(mock_root))

    check_dataset()

    dataset_dir = tmp_path / 'Dataset'
    dataset_file = dataset_dir / 'dataset.csv'

    assert dataset_dir.exists(), 'Dataset directory should be created.'
    assert dataset_dir.is_dir(), 'Dataset should be a directory.'

    assert dataset_file.exists(), 'Dataset file should be created.'
    assert dataset_file.is_file(), 'Dataset file should be a file.'

    with open(dataset_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["model", "serial number", "lot number", "grade", "stain", "scratch"], \
            'CSV header should match the expected fields.'


def test_controller_initialization(controller):
    assert controller.ui is not None, 'UI should be initialized.'
    assert 'openFile' in controller.actionDict, "Menu action 'openFile' should be initialized."
    assert controller.video_widget is not None, "Video widget should be initialized."
    assert controller.panel_widget is None, ("Panel widget should not be initialized until paned input lines are "
                                             "processed.")


def test_menu_bar(controller, qtbot):
    controller.init_menu_bar()
    menu_bar = controller.menuBar
    assert menu_bar is not None, 'Menu bar should be initialized.'

    action_open_file = controller.actionDict['openFile']
    assert action_open_file is not None, 'Action "openFile" should exist.'

    with qtbot.waitSignal(action_open_file.triggered, timeout=1000) as blocker:
        action_open_file.trigger()
    assert blocker.signal_triggered, 'Signal "triggered" should be connected to action "openFile".'


def test_panel_initialization(controller):
    mock_input_lines = [MagicMock(objectName=MagicMock(return_value=f"line_{i}")) for i in range(3)]
    controller.init_panel_base(mock_input_lines)
    for i, input_line in enumerate(mock_input_lines):
        name = f'line_{i}'
        assert name in controller.input_lines, f'Input line {name} should be initialized.'

    save_button = controller.panel_buttons['save_button']
    clear_button = controller.panel_buttons['clear_button']

    assert save_button is not None, 'Save button should be initialized.'
    assert clear_button is not None, 'Clear button should be initialized.'


# def test_main_flow(app, controller, qtbot):
#     mock_input_lines = [MagicMock(objectName=MagicMock(return_value=f"line_{i}")) for i in range(3)]
#     controller.init_panel_base(mock_input_lines)
#
#     detect_button = controller.video_buttons['detect_button']
#     qtbot.mouseClick(detect_button, Qt.LeftButton)
#
#
