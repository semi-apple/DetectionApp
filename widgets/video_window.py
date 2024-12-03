"""
Model Name: VideoWindow.py
Description: create a window widget to present camera information.
Author: Kun
Last Modified: 03 Jul 2024
"""
from PyQt5.QtCore import QObject, pyqtSlot, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog
# from exceptions.detection_exceptions import DetectionException
from interfaces.saver import ImageSaver
from interfaces.detection_functions import *
from .video_thread import VideoThread, VideoCapture
import cv2 as cv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import numpy as np

_widget_dir = os.path.dirname(os.path.abspath(__file__))

TRANSFER = {0: 'top', 1: 'bottom', 2: 'keyboard', 3: 'screen', 4: 'left', 5: 'right'}

def save_to_pdf(defects_list: list[tuple[list[Defect], int]], name: str):
    pdf_name = os.path.join(_widget_dir, f'../dataset/{name}.pdf')
    c = canvas.Canvas(pdf_name, pagesize=letter)
    width, height = letter

    y_position = height - 50
    idx = 0

    for defects, camera_port in defects_list:
        # idx of defect
        for d in defects:
            cv.imshow('d image', d.image)
            cv.waitKey()
            cv.destroyAllWindows()
            idx += 1
            c.drawString(50, y_position, f'Defect {idx + 1}: {d.cls} on {TRANSFER[camera_port]}')
            y_position -= 20

            # xyxy of defect
            x1, y1, x2, y2 = d.xyxy
            bbox_info = f'bbox: ({x1}, {y1}), ({x2}, {y1}), ({x1}, {y2}), ({x2}, {y2})'
            c.drawString(50, y_position, bbox_info)
            y_position -= 20

            # Process image directly in memory
            if isinstance(d.image, np.ndarray):
                pil_image = Image.fromarray(d.image)  # Convert NumPy array to PIL image
            else:
                raise ValueError("Image must be a NumPy array")

            img_reader = ImageReader(pil_image)  # Use PIL image directly

            # Calculate display size based on aspect ratio
            original_width, original_height = pil_image.size
            aspect_ratio = original_width / original_height

            display_width = 500
            display_height = display_width / aspect_ratio

            c.drawImage(img_reader, 50, y_position - display_height, width=display_width, height=display_height)
            y_position -= 220

            if y_position < 100:  # end of page
                c.showPage()
                y_position = height - 50

    c.save()
    print(f'PDF has saved to {pdf_name}')


class VideoBase(QObject):
    laptop_info = pyqtSignal(dict)

    def __init__(self, thread_labels=None, buttons=None, models=None):
        super().__init__()
        self.threads = []
        self.thread_labels = thread_labels
        self.buttons = buttons
        # self.models = models
        self.init_models(models)
        self.image_saver = ImageSaver()
        self.imgs = []

        self.buttons['detect_button'].clicked.connect(self.start_detection)
        self.buttons['capture_button'].clicked.connect(self.capture_images)
        # self.buttons['capture_button'].clicked.connect(self.capture_selected_images)
        self.buttons['stop_button'].clicked.connect(self.stop_detection)

    def init_models(self, models):
        self.top_bottom_model = models['top_bottom']
        self.lot_asset_barcode_model = models['lot_asset_barcode']
        self.logo_model = models['logo']
        self.lot_model = models['lot']
        self.serial_region_model = models['serial_region']
        self.serial_model = models['serial']
        self.barcode_model = models['barcode']
        self.keyboard_model = models['keyboard']
        self.screen_model = models['screen']

    def start_detection(self):
        for i, label in enumerate(self.thread_labels):
            video_capture = VideoCapture(i, label)
            video_capture.start()
            self.threads.append(video_capture)


        # for i in range(6):
        #     thread = VideoThread(i)
        #     thread.change_pixmap_signal.connect(getattr(self, f'set_image{i}'))
        #     thread.start()
        #     self.threads.append(thread)
        # ------------------------------------------------------------------------------ #
        # self.select_images()



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

    def detect_images(self, original_imgs: list) -> object:
        logo, lot, serial = '', '', ''
        detected_imgs = []
        detected_features = {}
        # detected_img = None
        detected_info = []
        defects_list = []
        models_list = [self.top_bottom_model, self.top_bottom_model, self.keyboard_model, self.screen_model]
        for img, camera_port in original_imgs:
            if img is None:
                continue
            if camera_port == 0:  # detect logo and lot number
                try:
                    lot, asset = detect_lot_asset_barcode(img, self.lot_asset_barcode_model)
                    logo = detect_logo(img, self.logo_model)
                    lot = detect_lot(img, self.lot_model)
                    detect_barcode(img, self.barcode_model)

                except LogoNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    logo = 'Logo_Not_Found'

                except LotNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    lot = 'Lot_Not_Found'

                except BarcodeNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')

                finally:
                    detected_features['logo'], detected_features['lot'] = logo, lot
                    print(f'Logo: {logo}, Lot Number: {lot}')

            if camera_port == 1:  # detect serial number
                try:
                    serial = detect_serial(img, self.serial_region_model, self.serial_model)
                    print(f'Serial Number: {serial}')

                except SerialNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    serial = 'Serial_Not_Found'

                finally:
                    detected_features['serial'] = serial

            # if camera_port == 2:
            #     detected_img, defects_counts = detect_keyboard(img, models_list[camera_port])
            # else:
            detected_img, defects_counts, defects = segment_with_sahi(img, 2, models_list[camera_port])
            if defects_counts is not None:
                detected_info.append((defects_counts, camera_port))
            if defects is not None:
                defects_list.append((defects, camera_port))
            detected_imgs.append((np.copy(detected_img), camera_port))

        detected_features['detected_info'] = detected_info
        return detected_imgs, detected_features, defects_list

    def capture_images(self):
        original_imgs = []

        # set default logo capture camera as 0
        for thread in self.threads:
            # if thread.running and thread.camera_port == 1: # on port 0
            if thread.running:
                original_img = thread.capture()  # original image
                original_imgs.append((np.copy(original_img), thread.camera_port))

        # capture images
        # self.save_raw_info(folder_name='raw_imgs', imgs=original_imgs)

        """
            Whether we need to store images over here, or we could store images on Control Panel, like:
            set signal, emit to Control Panel (raw images, cv images, detected features), store images 
            and detected feature on Control Panel.
            
            One good thing to do so is that if there is a detection error occurred, we can store images 
            with correct info by fixing problem manually.
             
            One bad thing is that it is not automatic.
        """

        detected_imgs, detected_features, defects_list= self.detect_images([np.copy(imgs), port] for imgs, port in original_imgs)
        lot = detected_features['lot']

        # self.save_raw_info(folder_name='original', imgs=original_imgs)
        # # cv_folder = lot + '_cv'
        # self.save_raw_info(folder_name='detected', imgs=detected_imgs)
        save_to_pdf(defects_list, lot)
        self.laptop_info.emit(detected_features)

    def stop_detection(self):
        for thread in self.threads:
            thread.stop()
        self.threads = []
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

        self.top_image_path = r'C:\Users\16379\Desktop\Dataset\dataset\images\train\image010.jpg'
        self.bottom_image_path = r'C:\Users\16379\Desktop\Dataset\dataset\images\train\image011.jpg'
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
            if img is None:
                continue
            original_imgs.append((np.copy(img), i))
            if i == 0:  # detect logo and lot number
                try:
                    logo = detect_logo(img, self.logo_model)
                    lot, asset = detect_lot_asset_barcode(img, self.lot_asset_barcode_model)
                    # lot = detect_lot(img, self.lot_model)
                    # detect_barcode(img, self.barcode_model)

                except LogoNotFoundException as e:
                    print(f'On port {i} -> {e}')
                    logo = 'Logo_Not_Found'

                except LotNumberNotFoundException as e:
                    print(f'On port {i} -> {e}')
                    lot = 'Lot_Not_Found'

                except BarcodeNotFoundException as e:
                    print(f'On port {i} -> {e}')

                finally:
                    detected_features['logo'], detected_features['lot'] = logo, lot
                    print(f'Logo: {logo}, Lot Number: {lot}')

            if i == 1:  # detect serial number
                try:
                    serial = detect_serial(img, self.serial_region_model, self.serial_model)
                    print(f'Serial Number: {serial}')

                except SerialNumberNotFoundException as e:
                    print(f'On port {i} -> {e}')
                    serial = 'Serial_Not_Found'

                finally:
                    detected_features['serial'] = serial

            # if i == 2:
            #     detected_img, defects_counts = detect_keyboard(img, models_list[i])
            # else:
            detected_img, defects_counts, defects = segment_with_sahi(img, 2, models_list[i])
            if defects_counts is not None:
                detected_features['defects'].append((defects_counts, i))
            detected_imgs.append((np.copy(detected_img), i))

        # self.save_raw_info(folder_name='original', imgs=original_imgs)
        # # cv_folder = lot + '_cv'
        # self.save_raw_info(folder_name='detected', imgs=detected_imgs)
        # self.laptop_info.emit(detected_features)