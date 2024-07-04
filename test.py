from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QImage

class ImageProcessor(QObject):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()

    def process_image(self, image_path):
        image = QImage(image_path)
        self.change_pixmap_signal.emit(image)

class ImageViewer:
    def __init__(self):
        self.thread = ImageProcessor()
        for i in range(3):
            self.thread.change_pixmap_signal.connect(getattr(self, f'set_image{i+1}'))

    def set_image1(self, image):
        print("Image 1 processed")

    def set_image2(self, image):
        print("Image 2 processed")

    def set_image3(self, image):
        print("Image 3 processed")

# Example usage
viewer = ImageViewer()
viewer.thread.process_image("path/to/image.jpg")
