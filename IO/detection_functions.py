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
from Exceptions.DetectionExceptions import (LotNumberNotFoundException, LogoNotFoundException,
                                            SerialNumberNotFoundException)

from PIL import Image
from plantcv import plantcv as pcv
import cv2 as cv
import numpy as np
import random
import pytesseract

# arrange an instance segmentation model for test
from sahi.utils.yolov8 import (
    download_yolov8s_model, download_yolov8s_seg_model
)

from sahi import AutoDetectionModel
from sahi.utils.cv import read_image
from sahi.utils.file import download_from_url
from sahi.predict import get_prediction, get_sliced_prediction, predict
from IPython.display import Image

from ultralytics import YOLO


def defects_segment(img, model):
    laptop_model_path = '/Users/kunzhou/Desktop/DetectionApp/Models/laptop.pt'
    laptop_model = YOLO(laptop_model_path)
    region_results = laptop_model(img)
    region_xyxy_list = region_results[0].boxes.xyxy.tolist()[0]
    rx1, ry1, rx2, ry2 = map(int, region_xyxy_list)
    laptop_region_img = img[ry1: ry2, rx1: rx2]

    classes = list(model.names.values())
    classes_ids = [classes.index(cls) for cls in classes]
    conf = 0.3

    # chip_id = classes.index('chip')  # id 0
    # dent_id = classes.index('dent')  # id 1
    # missing_id = classes.index('missing')  # id 2
    scratch_id = classes.index('scratch')  # id 3
    stain_id = classes.index('stain')  # id 4

    # defects_counts = [0, 0, 0, 0, 0]  # list index is defect id. For example, defects_count[0] is the number of chips
    # scratch_count, stain_count, chip_count, missing_count, dent_count = 0, 0, 0, 0, 0

    results = model.predict(laptop_region_img, conf=conf, imgsz=1280)
    colors = [random.choices(range(256), k=3) for _ in classes_ids]
    # print("Results:", results)

    img_area = laptop_region_img.shape[0] * laptop_region_img.shape[1]
    stain_area = 0
    try:
        for result in results:
            for mask, box in zip(result.masks.xy, result.boxes):
                # print(f"Mask: {mask}")
                # print(f"Mask shape: {mask.shape}")
                defect_id = int(box.cls[0])
                # defects_counts[defect_id] += 1

                if mask.size == 0 or len(mask.shape) != 2 or mask.shape[1] != 2:
                    # print("Error: Mask points do not have the correct shape")
                    continue

                points = np.int32(mask)
                # print(f"Points: {points}")
                # print(f"Points shape: {points.shape}")

                if defect_id == stain_id:
                    stain_area += cv.contourArea(points)

                color_number = classes_ids.index(defect_id)
                color = colors[color_number]
                cv.polylines(laptop_region_img, [points], isClosed=True, color=color, thickness=2)
                # cv.fillPoly(img, [points], colors[color_number])

                label = f"{classes[defect_id]}: {box.conf[0] * 100:.2f}%"
                x1, y1, _, _ = map(int, box.xyxy[0])
                cv.putText(laptop_region_img, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # for result in results:
        #     for boxes in result.boxes:
        #         x1, y1, x2, y2 = map(int, boxes.xyxy[0])
        #         defect_id = int(boxes.cls[0])
        #         color_number = classes_ids.index(defect_id)
        #         color = colors[color_number]
        #         thickness = 3
        #         cv.rectangle(img, (x1, y1), (x2, y2), color, thickness)
        #         label = f"{classes[defect_id]}: {boxes.conf[0]}"
        #         x1, y1, _, _ = map(int, boxes.xyxy[0])
        #         cv.putText(img, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        stain_area_percentage = (stain_area / img_area) * 100 if img_area > 0 else 0
        # print(f"Detected {defects_counts[scratch_id]} scratch(es)")
        print(f"Stain area percentage: {stain_area_percentage}%")
        cv.imshow('Image', laptop_region_img)
        cv.waitKey()
        cv.destroyAllWindows()
        return laptop_region_img

    except Exception as e:
        print(f"Error during segmentation: {e}")
        return laptop_region_img


def defects_detect(img, model):
    classes = list(model.names.values())
    classes_ids = [classes.index(cls) for cls in classes]

    conf = 0.2

    scratch_id = classes.index('scratch')
    stain_id = classes.index('stain')
    chip_id = classes.index('chip')
    missing_id = classes.index('missing')
    dent_id = classes.index('dent')

    scratch_count, stain_count = 0, 0

    results = model.predict(img, conf=conf)
    colors = [random.choices(range(256), k=3) for _ in classes_ids]
    # print("Results:", results)
    try:
        for result in results:
            for boxes in result.boxes:
                x1, y1, x2, y2 = map(int, boxes.xyxy[0])
                defect_id = int(boxes.cls[0])
                color_number = classes_ids.index(defect_id)
                color = colors[color_number]
                thickness = 3
                cv.rectangle(img, (x1, y1), (x2, y2), color, thickness)
                label = f"{classes[defect_id]}: {boxes.conf[0]}"
                x1, y1, _, _ = map(int, boxes.xyxy[0])
                cv.putText(img, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv.imshow('Image', img)
        cv.waitKey()
        cv.destroyAllWindows()
        return img

    except Exception as e:
        print(f"Error during segmentation: {e}")
        return img


def segment_with_sahi(original_img, num_blocks, model):
    laptop_model_path = '/Users/kunzhou/Desktop/DetectionApp/Models/laptop.pt'
    laptop_model = YOLO(laptop_model_path)

    region_results = laptop_model(original_img)

    region_xyxy_list = region_results[0].boxes.xyxy.tolist()[0]

    rx1, ry1, rx2, ry2 = map(int, region_xyxy_list)
    laptop_region_img = original_img[ry1: ry2, rx1: rx2]

    detection_model_seg = AutoDetectionModel.from_pretrained(
        model_type='yolov8',
        model=model,
        confidence_threshold=0.3,
        device='cpu',
    )

    h = laptop_region_img.shape[0]
    w = laptop_region_img.shape[1]
    # h = original_img.shape[0]
    # w = original_img.shape[1]
    W = num_blocks - 0.2 * (num_blocks - 1)
    results = get_sliced_prediction(
        laptop_region_img,
        # original_img,
        detection_model_seg,
        slice_height=int(h / W),
        slice_width=int(w / W),
        overlap_width_ratio=0.2,
        overlap_height_ratio=0.2,
    )
    classes = list(model.names.values())
    classes_ids = [classes.index(cls) for cls in classes]

    scratch_id = classes.index('scratch')  # id 3
    stain_id = classes.index('stain')  # id 4

    defects_counts = [0, 0]  # list index is defect id. For example, defects_count[0] is the number of chips
    scratch_count, stain_count = 0, 0

    colors = [random.choices(range(256), k=3) for _ in classes_ids]
    img_area = h * w
    stain_area = 0

    for prediction in results.object_prediction_list:
        for polygon in prediction.mask.segmentation:
            points = np.array(polygon).reshape((-1, 2))
            defect_id = prediction.category.id
            if defect_id == stain_id:
                stain_area += cv.contourArea(points)

            color_number = classes_ids.index(defect_id)
            color = colors[color_number]
            # cv.polylines(original_img, [points], isClosed=True, color=color, thickness=2)
            cv.polylines(laptop_region_img, [points], isClosed=True, color=color, thickness=2)
            # cv.fillPoly(img, [points], colors[color_number])

            label = f"{classes[defect_id]}: {prediction.score.value * 100:.2f}%"
            x1, y1, _, _ = prediction.bbox.to_xyxy()
            # cv.putText(original_img, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv.putText(laptop_region_img, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    stain_area_percentage = (stain_area / img_area) * 100 if img_area > 0 else 0
    print(f"Detected {defects_counts[scratch_id]} scratch(es)")
    print(f"Stain area percentage: {stain_area_percentage}%")
    cv.imshow('Image', laptop_region_img)
    # cv.imshow('Image', original_img)
    cv.waitKey()
    cv.destroyAllWindows()
    return laptop_region_img
    # return original_img


def detect_logo(original_img, logo_model):
    logo = ''
    max_conf = -1

    logo_results = logo_model(original_img)
    for i, box in enumerate(logo_results[0].boxes):
        if box.conf > max_conf:
            max_conf = box.conf
            logo = logo_model.names[int(box.cls)]
    if len(logo) == 0:
        raise LogoNotFoundException()

    return logo


def detect_lot(original_img, ocr_model):
    # detect lot number
    lot_results = ocr_model(original_img)

    try:
        xyxy_list = lot_results[0].boxes.xyxy[0].tolist()
    except Exception:
        raise LotNumberNotFoundException()

    x1, y1, x2, y2 = map(int, xyxy_list)
    lot_img = original_img[y1:y2, x1:x2]

    gray_img = cv.cvtColor(lot_img, cv.COLOR_BGR2GRAY)
    high_pass_kernel = np.array([[0, -1, 0],
                                 [-1, 5, -1],
                                 [0, -1, 0]])

    sharpened = cv.filter2D(gray_img, -1, high_pass_kernel)
    _, thresh = cv.threshold(sharpened, 180, 220, cv.THRESH_BINARY)
    cv.imshow('Lot image', thresh)
    cv.waitKey()
    cv.destroyAllWindows()

    lot_number = pytesseract.image_to_string(thresh)
    print(f'lot number: {lot_number}')

    return lot_number


def detect_serial(img, ser_region_model, ser_model):
    if img is None:
        print(f'Image is None')
        return
    region_results = ser_region_model(img)

    try:
        region_xyxy_list = region_results[1].boxes.xyxy.tolist()[0]
    except Exception as e:
        print('Cannot detect region with serial number, maybe caputre with wrong camera.')
        raise SerialNumberNotFoundException()

    rx1, ry1, rx2, ry2 = map(int, region_xyxy_list)
    serial_region_img = img[ry1: ry2, rx1: rx2]

    serial_results = ser_model(serial_region_img)

    try:
        serial_xyxy_list = serial_results[1].boxes.xyxy.tolist()[0]
    except Exception as e:
        print('Cannot detect region with serial number, maybe caputre with wrong camera.')
        raise SerialNumberNotFoundException()

    sx1, sy1, sx2, sy2 = map(int, serial_xyxy_list)
    serial_img = serial_region_img[sy1: sy2, sx1: sx2]

    gray_img = cv.cvtColor(serial_img, cv.COLOR_BGR2GRAY)
    high_pass_kernel = np.array([[0, -1, 0],
                                 [-1, 5, -1],
                                 [0, -1, 0]])

    sharpened = cv.filter2D(gray_img, -1, high_pass_kernel)
    _, thresh = cv.threshold(sharpened, 180, 220, cv.THRESH_BINARY)

    serial = pytesseract.image_to_string(thresh)

    return serial


if __name__ == "__main__":
    img = cv.imread('/Users/kunzhou/Desktop/DetectionApp/dataset/1306699/1306699_top.png')

    # segment_defect_test(img)
