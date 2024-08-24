"""
This script provides functionality for detecting objects and calculating the length of scratches
in images using OpenCV, PIL, and PlantCV libraries. It includes methods to perform edge detection,
measure the length of detected scratches, and visualize the detection results on frames.

Functions:
- scratch_len(img_cv, location): Calculate the length of scratches in a given image region.
- detected_edges(img_cv): Perform edge detection on an image.
- detect_objects_on_frame(frame, model): Detect objects on a given frame using a specified model.
- show_frame_with_detections(original_frame, detections): Visualize detected objects and their lengths on a frame.

Author: Kun
Last Modified: 10 Jul 2024
"""
from Exceptions.DetectionExceptions import LotNumberNotFoundException, LogoNotFoundException

from PIL import Image
from plantcv import plantcv as pcv
import cv2 as cv
import numpy as np
import random

# arrange an instance segmentation model for test
from sahi.utils.yolov8 import (
    download_yolov8s_model, download_yolov8s_seg_model
)

from sahi import AutoDetectionModel
from sahi.utils.cv import read_image
from sahi.utils.file import download_from_url
from sahi.predict import get_prediction, get_sliced_prediction, predict
from IPython.display import Image


def segment_defect(model, img):
    classes = list(model.names.values())
    classes_ids = [classes.index(cls) for cls in classes]

    conf = 0.2
    scratch_id = classes.index('scratch')
    stain_id = classes.index('stain')

    scratch_count, stain_count = 0, 0

    results = model.predict(img, conf=conf)
    colors = [random.choices(range(256), k=3) for _ in classes_ids]
    # print("Results:", results)
    try:
        for result in results:
            for mask, box in zip(result.masks.xy, result.boxes):
                # print(f"Mask: {mask}")
                # print(f"Mask shape: {mask.shape}")
                defect_id = int(box.cls[0])
                if defect_id == scratch_id:
                    scratch_count += 1
                elif defect_id == stain_id:
                    stain_count += 1
                else:
                    break

                if mask.size == 0 or len(mask.shape) != 2 or mask.shape[1] != 2:
                    print("Error: Mask points do not have the correct shape")
                    continue

                points = np.int32(mask)
                # print(f"Points: {points}")
                # print(f"Points shape: {points.shape}")

                color_number = classes_ids.index(int(box.cls[0]))
                cv.fillPoly(img, [points], colors[color_number])
        #
        # cv.imshow('Image', img)
        # cv.waitKey()
        return img, stain_count, stain_count

    except Exception as e:
        print(f"Error during segmentation: {e}")
        return img, stain_count, stain_count

def segment_defect_test(img):
    model_path = '/Users/kunzhou/Desktop/DetectionApp/Models/detect.pt'
    detection_model_seg = AutoDetectionModel.from_pretrained(
        model_type='yolov8',
        model_path=model_path,
        confidence_threshold=0.3,
        device='cpu',
    )

    h = img.shape[0]
    w = img.shape[1]

    result = get_sliced_prediction(
        img,
        detection_model_seg,
        slice_height=256,
        slice_width=256,
        overlap_width_ratio=0.2,
        overlap_height_ratio=0.2,
    )

    result.export_visuals(export_dir="demo_data/")

    Image("demo_data/prediction_visual.png")


def detect_logo_lot(original_img, logo_model, ocr_model, reader):
    logo = ''
    lot = ''

    max_conf = -1
    # detect logo
    logo_results = logo_model(original_img)
    for i, box in enumerate(logo_results[0].boxes):
        if box.conf > max_conf:
            max_conf = box.conf
            logo = logo_model.names[int(box.cls)]
    if len(logo) == 0:
        raise LogoNotFoundException()

    # detect lot number
    lot_results = ocr_model(original_img)

    try:
        xyxy = lot_results[0].boxes.xyxy[0].tolist()
    except Exception as e:
        raise LotNumberNotFoundException()
    x1, y1, x2, y2 = map(int, xyxy)

    lot_region = original_img[y1:y2, x1:x2]
    rotated_lot_region = cv.rotate(lot_region, cv.ROTATE_90_CLOCKWISE)
    gray_region = cv.cvtColor(rotated_lot_region, cv.COLOR_BGR2GRAY)
    _, lot_region_thresh = cv.threshold(gray_region, 200, 255, cv.THRESH_BINARY_INV)
    # cv.imshow('thresh', lot_region_thresh)
    # cv.waitKey()
    # cv.destroyAllWindows()
    lot_detections = reader.readtext(lot_region_thresh, allowlist='0123456789')
    for detection in lot_detections:
        lot += detection[1]

    return logo, lot


def detect_serial(img):
    return 'serial_test'


if __name__ == "__main__":
    img = cv.imread('/Users/kunzhou/Desktop/DetectionApp/dataset/1306699/1306699_top.png')

    segment_defect_test(img)
