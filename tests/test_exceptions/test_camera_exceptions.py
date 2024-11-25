from exceptions.camera_exceptions import CameraInitException
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)


def test_camera_init_exception_default_message():
    exception = CameraInitException()
    assert exception.message == 'Cannot Init Camera.', "Default message is 'Cannot Init Camera.'"


