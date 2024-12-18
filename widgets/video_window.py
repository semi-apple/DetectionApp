"""
Model Name: VideoWindow.py
Description: create a window widget to present camera information.
Author: Kun
Last Modified: 03 Jul 2024
"""
from PyQt5.QtCore import QObject, pyqtSlot, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog
# from exceptions.detection_exceptions import DetectionException
from interfaces.saver import ImageSaver, save_to_pdf
# from interfaces.detection_functions import *
from .video_thread import VideoThread
import cv2 as cv
import numpy as np
from .detection import DetectionThread
import time
from interfaces.classes import Defect


TRANSFER = {0: 'top', 1: 'bottom', 2: 'keyboard', 3: 'screen', 4: 'left', 5: 'right'}

class VideoBase(QObject):
    laptop_info = pyqtSignal(dict)  # Signal to emit detection results

    def __init__(self, thread_labels=None, buttons=None, models=None):
        """
        Initializes the VideoBase class.

        Args:
            thread_labels (list): List of PyQt5 labels for displaying video feeds.
            buttons (dict): Dictionary of buttons for starting/stopping detection.
            models (dict): Dictionary of detection models.
        """
        super().__init__()
        self.threads = []
        self.thread_labels = thread_labels
        self.buttons = buttons
        self.detection = DetectionThread(models)
        qThread = QThread()
        self.detection.moveToThread(qThread)
        self.detection.start()
        self.image_saver = ImageSaver()
        self.imgs = []

        self.buttons['detect_button'].clicked.connect(self.start_detection)
        self.buttons['capture_button'].clicked.connect(self.capture_images)
        # self.buttons['capture_button'].clicked.connect(self.capture_images)
        # self.buttons['capture_button'].clicked.connect(self.capture_selected_images)
        self.buttons['stop_button'].clicked.connect(self.stop_detection)
        self.detection.detected_info.connect(self.process_info)
        

    def start_detection(self):
        for i in range(1, 7):
            thread = VideoThread(i)
            
            if not thread.running:
                continue
            qThread = QThread()
            thread.moveToThread(qThread)
            thread.change_pixmap_signal.connect(getattr(self, f'set_image{i - 1}'))
            thread.start()
            self.threads.append((thread, qThread))
        # ------------------------------------------------------------------------------ #
        # self.select_images()

    def capture_images(self):
        original_imgs = []

        # set default logo capture camera as 0
        for thread, _ in self.threads:
            # if thread.running and thread.camera_port == 1: # on port 0
            if thread.running:
                original_img = thread.capture()  # original image
                original_imgs.append((np.copy(original_img), thread.camera_port))
                
        self.save_raw_info(folder_name='original', imgs=original_imgs)
        self.detection.add_images([(np.copy(img), port) for img, port in original_imgs])
    
    @pyqtSlot(tuple)
    def process_info(self, detected_info):
        detected_imgs, detected_features, defects_list = detected_info
        lot = detected_features['lot']
        self.save_raw_info(folder_name='detected', imgs=detected_imgs)
        save_to_pdf(detected_imgs, defects_list, lot)
        self.laptop_info.emit(detected_features)

    def stop_detection(self):
        for thread, qThread in self.threads:
            thread.stop()
            qThread.quit()
            qThread.wait()
        self.threads = []
        self.detection.running = False
        self.detection.stop()
        # time.sleep(1)
        for label in self.thread_labels:
            label.clear()

    def save_info(self, folder_name, lot, imgs):
        """save detected images"""
        self.image_saver.save(folder_name=folder_name, lot=lot, imgs=imgs)

    def save_raw_info(self, folder_name, imgs):
        """save original images"""
        self.image_saver.save_raw_imgs(folder_name=folder_name, imgs=imgs)

    @pyqtSlot(QImage)
    def set_image0(self, image):
        """Update thread labels based on the returned frame from thread.run()"""
        self.thread_labels[0].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[0].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image1(self, image):
        self.thread_labels[1].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[1].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image2(self, image):
        self.thread_labels[2].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[2].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image3(self, image):
        self.thread_labels[3].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[3].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image4(self, image):
        self.thread_labels[4].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[4].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image5(self, image):
        self.thread_labels[5].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[5].size(), Qt.KeepAspectRatio))

    def closeEvent(self, event):
        self.stop_detection()

# ----------------------------------- test ----------------------------------------------------------------- #  
    def display_image_on_label(self, image_path, label):
        img = cv.imread(image_path)
        self.imgs.append(img)
        img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        label_size = label.size()
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)

    def select_images(self):
        self.imgs = []
        dialog = QFileDialog()
        options = dialog.options()
        options |= QFileDialog.DontUseNativeDialog

        # self.top_image_path, _ = QFileDialog.getOpenFileName(None, "Select Top Image", "",
        #                                                      "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)",
        #                                                      options=options)
        # self.bottom_image_path, _ = QFileDialog.getOpenFileName(None, "Select Bottom Image", "",
        #                                                         "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)",
        #                                                         options=options)
        # self.keyboard_image_path, _ = QFileDialog.getOpenFileName(None, "Select Keyboard Image", "",
        #                                                           "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)",
        #                                                           options=options)
        # self.screen_image_path, _ = QFileDialog.getOpenFileName(None, "Select Screen Image", "",
        #                                                         "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)",
        #                                                         options=options)

        self.top_image_path = r'C:\Users\Kun\Desktop\demo\20240919124333_top.jpg'
        self.bottom_image_path = r'C:\Users\Kun\Desktop\demo\009A9537.JPG'
        # self.keyboard_image_path = r'C:\Users\Kun\Desktop\demo\keyboard\20241003122511_keyboard.jpg'

        if self.top_image_path:
            self.display_image_on_label(self.top_image_path, self.thread_labels[0])
        if self.bottom_image_path:
            self.display_image_on_label(self.bottom_image_path, self.thread_labels[1])
        # if self.keyboard_image_path:
        #     self.display_image_on_label(self.keyboard_image_path, self.thread_labels[2])
        # # if self.screen_image_path:
        #     self.display_image_on_label(self.screen_image_path, self.thread_labels[3])
        
    def capture_selected_images(self):
        logo, lot, serial = '', '', ''
        detected_imgs = []
        detected_features = {}
        detected_features['defects'] = []
        original_imgs = []
        models_list = [self.top_bottom_model, self.top_bottom_model, self.keyboard_model, self.screen_model]
        for i, img in enumerate(self.imgs):
            original_imgs.append((img, i + 1))
            
        detected_imgs, detected_features, defects_list= self.detect_images([np.copy(imgs), port] for imgs, port in original_imgs)
        lot = detected_features['lot']

        # self.save_raw_info(folder_name='original', imgs=original_imgs)
        # # cv_folder = lot + '_cv'
        # self.save_raw_info(folder_name='detected', imgs=detected_imgs)
        save_to_pdf(detected_imgs, defects_list, lot)
        self.laptop_info.emit(detected_features)


if __name__ == '__main__':
    img_path = '/Users/kunzhou/Desktop/demo/20240919121719_top.jpg'
    image = cv.imread(img_path)
    xyxy = (10, 10, 500, 500)
    xyxy2 = (100, 100, 117, 117)
    img2 = image[100: 117, 100: 117]
    img = image[10: 500, 10: 500]
    d1 = Defect(img, 'stain', xyxy)
    d2 = Defect(img2, 'stain', xyxy2)
    # cv.imshow('test', image)
    # cv.waitKey()
    # cv.destroyAllWindows()
    defects = [d1, ]
    save_to_pdf([(defects, 0), ([d2, ], 1)], 'test')
