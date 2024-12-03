"""
Define classes using in detection

Classes:
- Defect: Image and bbox of defects.

Author: Kun
Last Modified: 02 Dec 2024
"""


class Defect:
    def __init__(self, image, cls, xyxy):
        self.cls = cls
        self.image = image
        self.xyxy = xyxy


