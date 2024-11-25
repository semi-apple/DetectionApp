import pytest
from PyQt5.QtWidgets import QLineEdit, QApplication
from PyQt5.QtCore import Qt
from application import DetectionApp


@pytest.fixture(scope='module')
def app(qtbot):
    return QApplication([])


@pytest.fixture
def detection_app(qtbot):
    detection = DetectionApp()
    qtbot.addWidget(detection)
    return detection


def test_ui_initialization(detection_app):
    assert detection_app.ui is not None, 'UI components should be initialized.'
    # assert detection_app.findChildren(QLineEdit), 'QLineEdit should be exists.'


def test_signal_connection(detection_app, qtbot):
    with qtbot.waitSignal(detection_app.init_panel, timeout=1000) as blocker:
        detection_app.init_panel.emit(detection_app.findChildren(QLineEdit))
    assert blocker.signal_triggered, "Signal 'init_paned' should emitted and received correctly"


def test_start_detection(detection_app, qtbot):
    username = "test_user"
    level = 0

    detection_app.start_detection(username, level)

    assert detection_app.controller.username == username, 'Username should be set correctly.'
    assert detection_app.controller.level == level, 'Level should be set correctly.'

    app = QApplication.instance()
    primary_screen_geometry = app.screens()[0].geometry()
    assert detection_app.geometry() == primary_screen_geometry, 'Window geometry should match the primary screen.'


def test_close_application(detection_app, qtbot):
    detection_app.close()
    assert not detection_app.isVisible(), 'The app window should be closed.'




