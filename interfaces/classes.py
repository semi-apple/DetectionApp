"""
Define classes used in detection.

Classes:
- Defect: Represents a defect detected in an image, including its class, bounding box, and associated image.

Author: Kun
Last Modified: 02 Dec 2024
"""
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



