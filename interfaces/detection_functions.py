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
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2 as cv
import numpy as np
import random
import pytesseract
from exceptions.detection_exceptions import (LotNumberNotFoundException, LogoNotFoundException,
                                             SerialNumberNotFoundException, BarcodeNotFoundException, 
                                             AssetNumberNotFoundException)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from ultralytics import YOLO
from .classes import Defect

TRANSFER = {1: 'screen', 0: 'top', 2: 'left', 3: 'right', 4: 'screen', 5: 'keyboard'}
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f'script path: {script_dir}')
models_dir_path = os.path.join(script_dir, '../models')


def detect_lot_asset_barcode(original_img, model):
    """
       Detects lot number, asset number, and barcode in the image using a YOLO model.

       Args:
           original_img: The input image.
           detection_model: YOLO model for detection.
           classes: List of class names the model can detect (e.g., ['lot number', 'asset number', 'barcode']).

       Returns:
           Dictionary containing detected lot number, asset number, and barcode images or extracted text.
       """
    lot, asset = '', ''
    results = model(original_img)
    classes = list(model.names.values())
    print(classes)
    classes_ids = [classes.index(cls) for cls in classes]
    asset_id = classes.index('asset')
    lot_id = classes.index('lot')
    barcode_id = classes.index('barcode')
    for box in results[0].boxes:
        cls_id = int(box.cls[0].item())  # Class ID as integer
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Bounding box coordinates
        detected_region = original_img[y1-2: y2+2, x1-2: x2+2]  # Crop the detected region
        if cls_id == asset_id:
            asset = process_asset_number(detected_region)
        elif cls_id == lot_id:
            lot = process_lot_number(detected_region)
        # elif cls_id == barcode_id:
        #     process_barcode(detected_region)

    if lot is None:
        raise LotNumberNotFoundException()
    if asset is None:
        raise AssetNumberNotFoundException()
    # if asset is None:

    return lot, asset


def process_lot_number(lot_img):
    """Processes the lot number region."""
    gray_img = cv.cvtColor(lot_img, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray_img, 200, 250, cv.THRESH_BINARY)

    # cv.imshow("Barcode Image", thresh)
    # cv.waitKey()
    # cv.destroyAllWindows()
    lot_number = pytesseract.image_to_string(thresh)
    print(f"Detected lot number: {lot_number}")

    return lot_number


def process_asset_number(asset_img):
    """Processes the asset number region."""
    gray_img = cv.cvtColor(asset_img, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray_img, 200, 250, cv.THRESH_BINARY)

    # cv.imshow("Barcode Image", thresh)
    # cv.waitKey()
    # cv.destroyAllWindows()
    asset_number = pytesseract.image_to_string(thresh)
    print(f"Detected asset number: {asset_number}")

    return asset_number


def process_barcode(barcode_img):
    """Processes the barcode region."""
    # You can use specialized barcode reading libraries (e.g., `pyzbar` or `pytesseract`)
    cv.imshow("Barcode Image", barcode_img)
    cv.waitKey()
    cv.destroyAllWindows()

    return barcode_img


def defects_segment(img, model):
    laptop_model_path = os.path.join(models_dir_path, 'laptop.pt')
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
        # cv.imshow('Image', laptop_region_img)
        # cv.waitKey()
        # cv.destroyAllWindows()
        detected_img = draw_multiple_rectangles(laptop_region_img, 1)
        return detected_img

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


def detect_keyboard(original_img, model):
    # detection_model_seg = AutoDetectionModel.from_pretrained(
    #     model_type='yolov8',
    #     model=model,
    #     confidence_threshold=0.3,
    #     device='cuda',
    # )

    # h, w = original_img.shape[:2]
    # # h = original_img.shape[0]
    # # w = original_img.shape[1]
    # W = num_blocks - 0.2 * (num_blocks - 1)
    # results = get_sliced_prediction(
    #     original_img,
    #     # original_img,
    #     detection_model_seg,
    #     slice_height=int(h / W),
    #     slice_width=int(w / W),
    #     overlap_width_ratio=0.2,
    #     overlap_height_ratio=0.2,
    # )
    conf = 0.5
    classes = list(model.names.values())
    classes_ids = [classes.index(cls) for cls in classes]

    # print(f'classes: {classes}')
    # print(f'classes_ids: {classes_ids}')

    results = model.predict(original_img, conf=conf, imgsz=1280)
    colors = [random.choices(range(256), k=3) for _ in classes_ids]
    # print("Results:", results)
    defects_counts = [0, 0, 0, 0,
                      0]  # list index is defect id. For example, defects_count[0] is the number of scratches

    img_area = original_img.shape[0] * original_img.shape[1]
    stain_area = 0
    for result in results:
        for mask, box in zip(result.masks.xy, result.boxes):
            # print(f"Mask: {mask}")
            # print(f"Mask shape: {mask.shape}")
            defect_id = int(box.cls[0])
            defects_counts[defect_id] += 1

            if mask.size == 0 or len(mask.shape) != 2 or mask.shape[1] != 2:
                # print("Error: Mask points do not have the correct shape")
                continue

            points = np.int32(mask)

            if classes[defect_id] == 'stain':
                stain_area += cv.contourArea(points)

            color_number = classes_ids.index(defect_id)
            color = colors[color_number]
            cv.polylines(original_img, [points], isClosed=True, color=color, thickness=2)
            # cv.fillPoly(img, [points], colors[color_number])

            label = f"{classes[defect_id]}: {box.conf[0] * 100:.2f}%"
            x1, y1, _, _ = map(int, box.xyxy[0])
            cv.putText(original_img, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # cv.imshow('Image', original_img)
    # # cv.imshow('Image', original_img)
    # cv.waitKey()
    # cv.destroyAllWindows()
    detected_img = draw_multiple_rectangles(original_img, 1)
    return detected_img, None
    # return original_img


def segment_with_sahi(original_img, num_blocks, model):
    laptop_model_path = os.path.join(models_dir_path, 'laptop.pt')
    laptop_model = YOLO(laptop_model_path)

    region_results = laptop_model(original_img)

    region_xyxy_list = region_results[0].boxes.xyxy.tolist()[0]

    rx1, ry1, rx2, ry2 = map(int, region_xyxy_list)
    laptop_region_img = original_img[ry1: ry2, rx1: rx2]
    cp_laptop_region_img = np.copy(laptop_region_img)

    detection_model_seg = AutoDetectionModel.from_pretrained(
        model_type='yolov8',
        model=model,
        confidence_threshold=0.3,
        device='cuda',
    )

    h, w = laptop_region_img.shape[:2]
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

    scratch_id = classes.index('scratch')
    stain_id = classes.index('stain')

    defects_counts = [0, 0]  # list index is defect id. For example, defects_count[0] is the number of scratches
    scratch_count, stain_count = 0, 0

    colors = [random.choices(range(256), k=3) for _ in classes_ids]
    img_area = h * w
    stain_area = 0

    defects = []

    for prediction in results.object_prediction_list:
        for polygon in prediction.mask.segmentation:
            points = np.array(polygon).reshape((-1, 2))
            defect_id = prediction.category.id
            if defect_id == stain_id:
                stain_count += 1
                stain_area += cv.contourArea(points)

            if defect_id == scratch_id:
                scratch_count += 1

            color_number = classes_ids.index(defect_id)
            color = colors[color_number]
            x1, y1, x2, y2 = prediction.bbox.to_xyxy()
            # store defect image
            defect_img = cp_laptop_region_img[y1: y2, x1: x2]
            d = Defect(image=defect_img, cls=classes[defect_id], xyxy=(x1, y1, x2, y2))
            defects.append(d)

            # cv.polylines(original_img, [points], isClosed=True, color=color, thickness=2)
            cv.polylines(laptop_region_img, [points], isClosed=True, color=color, thickness=2)
            # cv.fillPoly(img, [points], colors[color_number])

            label = f"{classes[defect_id]}: {prediction.score.value * 100:.2f}%"
            # cv.putText(original_img, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv.putText(laptop_region_img, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    defects = filter_defects(defects, min_area=256, iou_threshold=0.9)
    stain_area_percentage = (stain_area / img_area) * 100 if img_area > 0 else 0
    print(f"Detected {defects_counts[scratch_id]} scratch(es)")
    print(f"Stain area percentage: {stain_area_percentage}%")
    # cv.imshow('detected', laptop_region_img)
    # for d in defects:
    #     cv.imshow('defects', d.image)
    #     cv.waitKey()
    #     cv.destroyAllWindows()

    # cv.imshow('Image', original_img)
    # cv.waitKey()
    # cv.destroyAllWindows()
    detected_img = draw_multiple_rectangles(laptop_region_img, 1)
    defects_counts[0] = scratch_count
    defects_counts[1] = stain_count
    return detected_img, defects_counts, defects


def filter_defects(defects, min_area=1000, iou_threshold=0.5):
    """Remove a defects which is too small or redundant.

    Args:
        defects (list[Defect]): defects list
        min_area (int): min area
        iou_threshold (float): IoU

    Returns:
        list[Defect]: filtered defects list。
    """
    # remove defects that are very small
    filtered_defects = [d for d in defects if (d.xyxy[2] - d.xyxy[0]) * (d.xyxy[3] - d.xyxy[1]) >= min_area]

    # remove redundant defects
    final_defects = []
    visited = set()  # stores the defects that has been visited

    for i, d1 in enumerate(filtered_defects):
        if i in visited:
            continue

        duplicates = [d1]  # store duplicated defects
        for j, d2 in enumerate(filtered_defects):
            if i != j and calculate_iou(d1.xyxy, d2.xyxy) > iou_threshold:
                duplicates.append(d2)
                visited.add(j)  # marked as processed

        # remain the highest marks
        best_defect = max(duplicates, key=lambda d: (d.xyxy[2] - d.xyxy[0]) * (d.xyxy[3] - d.xyxy[1]))
        final_defects.append(best_defect)
        
    # Get the top 5 largest defects
    top_5_defects = sorted(final_defects, key=lambda d: (d.xyxy[2] - d.xyxy[0]) * (d.xyxy[3] - d.xyxy[1]), reverse=True)[:5]

    return top_5_defects


def calculate_iou(box1, box2):
    """Calculate IoU of two defects

    Args:
        box1 (tuple[int]): bbox of the first defect (x1, y1, x2, y2)。
        box2 (tuple[int]): bbox of the second defect (x1, y1, x2, y2)。

    Returns:
        float: IoU
    """
    x1_inter = max(box1[0], box2[0])
    y1_inter = max(box1[1], box2[1])
    x2_inter = min(box1[2], box2[2])
    y2_inter = min(box1[3], box2[3])

    inter_area = max(0, x2_inter - x1_inter) * max(0, y2_inter - y1_inter)

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union_area = box1_area + box2_area - inter_area

    if union_area == 0:
        return 0

    return inter_area / union_area


def detect_barcode(original_img, barcode_model):
    """Archived"""
    # detect lot number
    barcode_results = barcode_model(original_img)

    try:
        xyxy_list = barcode_results[0].boxes.xyxy[0].tolist()
    except Exception:
        raise BarcodeNotFoundException()

    x1, y1, x2, y2 = map(int, xyxy_list)
    barcode_img = original_img[y1: y2, x1: x2]
    cv.imshow('barcode', barcode_img)
    cv.waitKey()
    cv.destroyAllWindows()


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
    """Archived"""
    # detect lot number
    lot_results = ocr_model(original_img)

    try:
        xyxy_list = lot_results[0].boxes.xyxy[0].tolist()
    except Exception:
        raise LotNumberNotFoundException()

    x1, y1, x2, y2 = map(int, xyxy_list)
    lot_img = original_img[y1 - 5: y2 + 5, x1 - 2: x2 + 2]

    gray_img = cv.cvtColor(lot_img, cv.COLOR_BGR2GRAY)
    high_pass_kernel = np.array([[0, -1, 0],
                                 [-1, 5, -1],
                                 [0, -1, 0]])

    # sharpened = cv.filter2D(gray_img, -1, high_pass_kernel)
    _, thresh = cv.threshold(gray_img, 150, 200, cv.THRESH_BINARY)
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
        region_xyxy_list = region_results[0].boxes.xyxy.tolist()[0]
    except Exception as e:
        print('Cannot detect region with serial number, maybe caputre with wrong camera.')
        raise SerialNumberNotFoundException()

    rx1, ry1, rx2, ry2 = map(int, region_xyxy_list)
    serial_region_img = img[ry1: ry2, rx1: rx2]
    # cv.imshow('serial region', serial_region_img)
    # cv.waitKey()
    # cv.destroyAllWindows()

    serial_results = ser_model(serial_region_img)

    try:
        serial_xyxy_list = serial_results[0].boxes.xyxy.tolist()[0]
    except Exception as e:
        print('Cannot detect region with serial number, maybe caputre with wrong camera.')
        raise SerialNumberNotFoundException()

    sx1, sy1, sx2, sy2 = map(int, serial_xyxy_list)
    serial_img = serial_region_img[sy1 - 5: sy2 + 5, sx1 - 10: sx2 + 10]
    # cv.imshow('serial', serial_img)
    # cv.waitKey()
    # cv.destroyAllWindows()

    gray_img = cv.cvtColor(serial_img, cv.COLOR_BGR2GRAY)
    # high_pass_kernel = np.array([[0, -1, 0],
    #                              [-1, 5, -1],
    #                              [0, -1, 0]])

    # sharpened = cv.filter2D(gray_img, -1, high_pass_kernel)
    _, thresh = cv.threshold(gray_img, 180, 220, cv.THRESH_BINARY + cv.THRESH_OTSU)
    cv.imshow('serial', thresh)
    cv.waitKey()
    cv.destroyAllWindows()

    serial = pytesseract.image_to_string(thresh)
    print(f'serial: {serial}')

    return serial


def draw_multiple_rectangles(image, port):
    drawing = False
    start_point = (-1, -1)
    rectangles = []

    target_width = 1280
    target_height = 860

    image = cv.resize(image, (target_width, target_height))

    def draw_rectangle(event, x, y, flags, param):
        nonlocal drawing, start_point, rectangles

        if event == cv.EVENT_LBUTTONDOWN:
            drawing = True
            start_point = (x, y)

        elif event == cv.EVENT_MOUSEMOVE:
            if drawing:
                end_point = (x, y)
                temp_image = image.copy()
                cv.rectangle(temp_image, start_point, end_point, (0, 255, 0), 2)
                for rect in rectangles:
                    cv.rectangle(temp_image, rect[0], rect[1], (0, 255, 0), 2)
                cv.imshow('Image', temp_image)

        elif event == cv.EVENT_LBUTTONUP:
            drawing = False
            end_point = (x, y)
            rectangles.append((start_point, end_point))

            temp_image = image.copy()
            for rect in rectangles:
                cv.rectangle(temp_image, rect[0], rect[1], (0, 255, 0), 2)
            cv.imshow('Image', temp_image)

    temp_image = image.copy()

    cv.namedWindow('Image')
    cv.setMouseCallback('Image', draw_rectangle)

    cv.imshow('Image', image)

    while True:
        key = cv.waitKey(1) & 0xFF
        if key == ord(' '):
            break

    cv.destroyAllWindows()

    for rect in rectangles:
        cv.rectangle(image, rect[0], rect[1], (0, 255, 0), 2)

    return image


if __name__ == "__main__":
    img = cv.imread('/Users/kunzhou/Desktop/demo/20240919121824_top.jpg')
    model = YOLO('/Users/kunzhou/Desktop/DetectionApp/models/lot_asset_barcode.pt')
    sahi_model = YOLO('/Users/kunzhou/Desktop/DetectionApp/models/top_bottom.pt')
    # ocr_model = YOLO(r'C:\Users\16379\Desktop\DetectionApp\models\lot.pt')
    # lot, asset = detect_lot_asset_barcode(img, model)
    segment_with_sahi(img, 2, sahi_model)
    # lot = detect_lot(img, ocr_model=ocr_model)
    # print(lot)
    # print(lot, asset)
