"""
This file defines exceptions that would happen when init camera.

Classes:
- CameraInitException: Cannot init camera
"""


class CameraInitException(Exception):
    """
    Exception raised for error when camera is not initiated correctly.

    Attributes:
        message -- explanation of the error.
    """

    def __init__(self, message='Cannot Init Camera.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


