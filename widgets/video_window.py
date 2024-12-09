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
from interfaces.saver import ImageSaver
from interfaces.detection_functions import *
from .video_thread import VideoThread
import cv2 as cv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import numpy as np

_widget_dir = os.path.dirname(os.path.abspath(__file__))

TRANSFER = {0: 'top', 1: 'bottom', 2: 'keyboard', 3: 'screen', 4: 'left', 5: 'right'}

def save_to_pdf(detected_imgs: list[tuple], defects_list: list[tuple[list[Defect], int]], name: str):
    """
    Generates a PDF report summarizing the detected defects and includes full detected images.

    Args:
        detected_imgs (list[tuple]): List of detected images and their associated camera ports.
        defects_list (list[tuple[list[Defect], int]]): Detected defects grouped by camera port.
        name (str): Name of the PDF file.
    """
    name = name.strip('\n')
    pdf_name = os.path.join(_widget_dir, f'../dataset/{name}.pdf')
    c = canvas.Canvas(pdf_name, pagesize=letter)
    width, height = letter

    y_position = height - 50
    idx = 0

    for defects, camera_port in defects_list:
        detected_img = None
        for img, port in detected_imgs:
            if port == camera_port:
                detected_img = img

        # Insert detected_img at the beginning
        if detected_img is not None:
            if isinstance(detected_img, np.ndarray):
                pil_detected_img = Image.fromarray(detected_img)  # Convert NumPy array to PIL image
            else:
                raise ValueError("Detected image must be a NumPy array")

            detected_img_reader = ImageReader(pil_detected_img)  # Use PIL image directly
            original_width, original_height = pil_detected_img.size
            aspect_ratio = original_width / original_height
            display_width = 500
            display_height = display_width / aspect_ratio
            if y_position - display_height < 100:  # end of page
                c.showPage()
                y_position = height - 50
            # title 
            c.drawString(50, y_position, f'Surface: {TRANSFER[port]}')
            y_position -= 20
            # image
            c.drawImage(detected_img_reader, 50, y_position - display_height, width=display_width, height=display_height)
            y_position -= (display_height + 20)

            if y_position < 100:  # Check for end of page
                c.showPage()
                y_position = height - 50
                
        # idx of defect
        for d in defects:
            c.drawString(50, y_position, f'Defect {idx + 1}: {d.cls}')
            idx += 1
            y_position -= 20

            # xyxy of defect
            x1, y1, x2, y2 = d.xyxy
            # bbox_info = f'bbox: ({x1}, {y1}), ({x2}, {y1}), ({x1}, {y2}), ({x2}, {y2})'
            # c.drawString(50, y_position, bbox_info)
            # y_position -= 20

            # Process image directly in memory
            if isinstance(d.image, np.ndarray):
                pil_image = Image.fromarray(d.image)  # Convert NumPy array to PIL image
            else:
                raise ValueError("Image must be a NumPy array")

            img_reader = ImageReader(pil_image)  # Use PIL image directly

            # Calculate display size based on aspect ratio
            original_width, original_height = pil_image.size

            if original_width < 500:
                c.drawImage(img_reader, 50, y_position - original_height, width=original_width, height=original_height)
                y_position -= (original_height + 20)
            else:
                aspect_ratio = original_width / original_height
                display_width = 500
                display_height = display_width / aspect_ratio
                c.drawImage(img_reader, 50, y_position - display_height, width=display_width, height=display_height)
                y_position -= (display_height + 20)

            if y_position < 100:  # end of page
                c.showPage()
                y_position = height - 50

    c.save()
    print(f'PDF has saved to {pdf_name}')


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
        # self.lot_model = models['lot']
        self.serial_region_model = models['serial_region']
        self.serial_model = models['serial']
        # self.barcode_model = models['barcode']
        self.keyboard_model = models['keyboard']
        self.screen_model = models['screen']

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

    def detect_images(self, original_imgs: list) -> object:
        """
        Performs detection on the captured images.

        Args:
            original_imgs (list): List of original images captured by cameras.

        Returns:
            tuple: Detected images, features, and defect lists.
        """
        logo, lot, serial = '', '', ''
        detected_imgs = []
        detected_features = {}
        # detected_img = None
        detected_info = []
        defects_list = []
        models_list = [self.top_bottom_model, self.top_bottom_model, self.keyboard_model, self.screen_model]
        for img, camera_port in original_imgs:
            # camera_port += 1
            if img is None:
                continue
            # cv.imshow(f"image", img)
            # cv.waitKey()
            # cv.destroyAllWindows()
            print(f"detect_images running in thread: {threading.current_thread().name}")
            if camera_port == 1:  # detect logo and lot number
                logo, lot, asset = None, None, None  # Initialize variables
                # Detect logo
                try:
                    logo = detect_logo(img, self.logo_model)
                except LogoNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    logo = 'Logo_Not_Found'

                # Detect lot number
                try:
                    lot, asset = detect_lot_asset_barcode(img, self.lot_asset_barcode_model)
                except LotNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    lot = 'Lot_Not_Found'
                    asset = 'Asset_Not_Found'
                except AssetNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    asset = 'Asset_Not_Found'
                
                detected_features['logo'], detected_features['lot'], detected_features['asset'] = \
                    logo, lot, asset
                print(f'Logo: {logo}, Lot Number: {lot}')

            if camera_port == 2:  # detect serial number
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
            detected_img, defects_counts, defects = segment_with_sahi(img, 2, models_list[camera_port - 1])
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
        for thread, _ in self.threads:
            # if thread.running and thread.camera_port == 1: # on port 0
            if thread.running:
                original_img = thread.capture()  # original image
                original_imgs.append((np.copy(original_img), thread.camera_port))

        # self.top_image_path = r'C:\Users\Kun\Desktop\demo\20240919124333_top.jpg'
        # self.bottom_image_path = r'C:\Users\Kun\Desktop\demo\009A9537.JPG'
        # original_imgs.append((np.copy(cv.imread(self.top_image_path)), 1))
        # original_imgs.append((np.copy(cv.imread(self.bottom_image_path)), 2))

        # capture images
        # self.save_raw_info(folder_name='raw_imgs', imgs=original_imgs)
        # for img, port in original_imgs:
        #     cv.imshow(f"Port {port}", img)
        #     cv.waitKey()
        #     cv.destroyAllWindows()
        
        # return

        """
            Whether we need to store images over here, or we could store images on Control Panel, like:
            set signal, emit to Control Panel (raw images, cv images, detected features), store images 
            and detected feature on Control Panel.
            
            One good thing to do so is that if there is a detection error occurred, we can store images 
            with correct info by fixing problem manually.
             
            One bad thing is that it is not automatic.
        """

        detected_imgs, detected_features, defects_list = self.detect_images([np.copy(imgs), port] for imgs, port in original_imgs)
        lot = detected_features['lot']

        # self.save_raw_info(folder_name='original', imgs=original_imgs)
        # # cv_folder = lot + '_cv'
        # self.save_raw_info(folder_name='detected', imgs=detected_imgs)
        save_to_pdf(detected_imgs, defects_list, lot)
        self.laptop_info.emit(detected_features)

    def stop_detection(self):
        for thread, qThread in self.threads:
            thread.stop()
            qThread.quit()
            qThread.wait()
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
