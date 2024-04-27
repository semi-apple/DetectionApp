from PyQt5.QtCore import pyqtSlot
from IO.detection_functions import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, camera_port=0, model=None):
        super().__init__()
        self.camera_port = camera_port
        self.model = model
        self.running = True

    def run(self):
        cap = cv.VideoCapture(self.camera_port)
        while self.running:
            ret, frame = cap.read()
            if ret:
                detections = detect_objects_on_frame(frame, self.model)
                show_frame_with_detections(frame, detections)
                qt_image = self.convert_cv_qt(frame)
                self.change_pixmap_signal.emit(qt_image)
            else:
                self.running = False
        cap.release()

    def convert_cv_qt(self, cv_img):
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return convert_to_Qt_format

    def stop(self):
        self.running = False
        self.wait()


@pyqtSlot(np.ndarray)
def update_image(cv_img, label):
    rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    p = convert_to_Qt_format.scaled(640, 480, aspectRatioMode=Qt.IgnoreAspectRatio)
    pixmap = QPixmap.fromImage(p)
    label.setPixmap(pixmap)

