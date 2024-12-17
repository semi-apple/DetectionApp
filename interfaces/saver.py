"""
Model Name: ImageSaver.py
Description: Handles saving images into the dataset directory.

Classes:
- ImageSaver: Provides functionality to save processed and raw images into organized directories.

Author: Kun
Last Modified: 03 Jul 2024
"""
import os
import cv2 as cv
from datetime import datetime
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from interfaces.classes import Defect
from reportlab.lib.pagesizes import letter

_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
# Mapping of camera ports to descriptive names
TRANSFER = {0: 'top', 1: 'bottom', 2: 'left', 3: 'right', 4: 'screen', 5: 'keyboard'}

def save_to_pdf(detected_imgs: list[tuple], defects_list: list[tuple[list[Defect], int]], name: str):
    """
    Generates a PDF report summarizing the detected defects and includes full detected images.

    Args:
        detected_imgs (list[tuple]): List of detected images and their associated camera ports.
        defects_list (list[tuple[list[Defect], int]]): Detected defects grouped by camera port.
        name (str): Name of the PDF file.
    """
    name = name.strip('\n')
    pdf_name = os.path.join(_root, f'dataset/{name}.pdf')
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


class ImageSaver:
    """
    A class to handle saving images into organized dataset directories.

    Attributes:
        root_directory (str): The root directory of the project.
        save_directory (str): The directory where images will be saved.
    """
    def __init__(self, save_directory='dataset'):
        """
        Initialize the ImageSaver.

        Args:
            save_directory (str): Name of the folder to store the dataset. Default is 'dataset'.
        """
        self.root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.save_directory = os.path.join(self.root_directory, save_directory)
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def save(self, folder_name, lot, imgs):
        """
        Save processed images into a specific folder.

        Args:
            folder_name (str): Name of the sub-folder to save the images.
            lot (str): Identifier for the lot (e.g., lot number).
            imgs (list[tuple]): List of tuples containing the image and corresponding camera port.
        """
        save_directory = os.path.join(self.save_directory, folder_name)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Create the file path
        for image, camera_port in imgs:
            if image is None:
                break
            file_path = os.path.join(save_directory, f'{lot}_{TRANSFER[camera_port]}.jpg')

            # Save the image
            cv.imwrite(file_path, image)
            print(f'Saved image: {file_path}')

    def save_raw_imgs(self, folder_name, imgs):
        """
        Save original images into a timestamped folder (for test).

        Args:
            folder_name (str): Name of the sub-folder to save the images.
            imgs (list[tuple]): List of tuples containing the image and corresponding camera port.
        """
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")

        save_directory = os.path.join(self.save_directory, f'{folder_name}_{formatted_time}')
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Create the file path
        for image, camera_port in imgs:
            if image is None:
                break

            assert isinstance(image, np.ndarray), "Image is not a numpy array"
            file_path = os.path.join(save_directory, f'{formatted_time}_{TRANSFER[camera_port]}.jpg')

            # Save the image
            cv.imwrite(file_path, image)
            print(f'Saved image: {file_path}')


if __name__ == '__main__':
    saver = ImageSaver()
    lot = 'test001'
    imgs = []
    img = cv.imread('../image001.jpg')
    imgs.append(img)
    saver.save(lot, lot, imgs)
