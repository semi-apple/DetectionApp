import sys
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from UI import *
from IO import ImageSaver
import numpy as np


class CameraThread(QtCore.QThread):
    image_update = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, camera_index, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.capture = None
        self.active = False

    def run(self):
        self.capture = cv2.VideoCapture(self.camera_index)
        if self.capture.isOpened():
            self.active = True
        else:
            self.active = False
            print(f'Cannot detect camera {self.camera_index}, make sure the camera is installed correctly.')

        while self.active:
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                p = QtGui.QPixmap.fromImage(convert_to_qt_format)
                self.image_update.emit(p)

        self.capture.release()

    def stop(self):
        self.active = False
        self.capture.release()
        # self.quit()

    def capture_image(self):
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                return frame
        return None


class VideoBase:
    def __init__(self, thread_labels, buttons, models):
        self.thread_labels = thread_labels
        self.buttons = buttons
        self.models = models
        self.threads = []
        self.image_saver = ImageSaver()

    def start_detection(self):
        self.threads = []
        available_cameras = 6
        for i in range(available_cameras):
            thread = CameraThread(camera_index=i)
            thread.image_update.connect(self.thread_labels[i].setPixmap)
            self.threads.append(thread)
            thread.start()

    def capture_images(self):
        original_imgs = []
        for thread in self.threads:
            if thread.active:
                img = thread.capture_image()
                original_imgs.append(np.copy(img))

        self.image_saver.save_raw_imgs(folder_name='raw_imgs', imgs=original_imgs)

    # def stop_detection(self):
    #     for thread in self.threads:
    #         thread.stop()


class MainWindowController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.thread_labels = []
        self.video_buttons = {}
        self.models = []  # Placeholder for models if needed

        self.init_video_base()

        self.video_widget.buttons['detect_button'].clicked.connect(self.video_widget.start_detection)
        self.video_widget.buttons['capture_button'].clicked.connect(self.video_widget.capture_images)
        self.video_widget.buttons['stop_button'].clicked.connect(self.stop_detection)

    def init_video_base(self):
        for i in range(6):
            video_thread = getattr(self.ui, f'video_thread_{i+1}')
            video_thread.setMinimumSize(300, 250)
            video_thread.setMaximumSize(500, 340)
            video_thread.setScaledContents(True)
            self.thread_labels.append(video_thread)

        detect_button = getattr(self.ui, 'start_detection_button')
        self.video_buttons['detect_button'] = detect_button

        capture_button = getattr(self.ui, 'capture_images_button')
        self.video_buttons['capture_button'] = capture_button

        stop_button = getattr(self.ui, 'stop_detection_button')
        self.video_buttons['stop_button'] = stop_button

        self.video_widget = VideoBase(thread_labels=self.thread_labels,
                                      buttons=self.video_buttons, models=self.models)

    def stop_detection(self):
        for thread in self.video_widget.threads:
            thread.stop()
        self.video_widget.threads = []
        for label in self.thread_labels:
            label.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindowController()
    main_window.show()
    sys.exit(app.exec_())
