import pytest
from exceptions.camera_exceptions import CameraInitException


def test_camera_init_exception_default_message():
    exception = CameraInitException()
    assert exception.message == 'Cannot Init Camera.', "Default message is 'Cannot Init Camera.'"


