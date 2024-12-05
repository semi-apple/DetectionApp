"""
Define classes used in detection.

Classes:
- Defect: Represents a defect detected in an image, including its class, bounding box, and associated image.

Author: Kun
Last Modified: 02 Dec 2024
"""
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import cv2 as cv
import numpy as np


class Defect:
    """
    A class to represent a detected defect.

    Attributes:
        cls (str): The class of the defect (e.g., 'scratch', 'stain').
        image (numpy.ndarray): The image crop corresponding to the defect.
        xyxy (tuple): The bounding box of the defect in the format (x1, y1, x2, y2).
    """
    def __init__(self, image, cls, xyxy):
        self.cls = cls
        self.image = image
        self.xyxy = xyxy


class GUIHandler(QObject):
    display_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.display_signal.connect(self.display_image)

    @pyqtSlot(np.ndarray)
    def display_image(self, image):
        """Show image in main thread"""
        cv.imshow('Image Display', image)
        cv.waitKey()
        cv.destroyAllWindows()

