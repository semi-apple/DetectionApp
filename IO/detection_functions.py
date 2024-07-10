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

from PIL import Image
from plantcv import plantcv as pcv
import cv2 as cv
import numpy as np


def scratch_len(img_cv, location):
    # Calculate the scratch length
    x1, y1, x2, y2 = location
    asset_img = img_cv[y1:y2, x1:x2]
    edges = detected_edges(asset_img)
    _, edges_bin = cv.threshold(edges, 40, 255, cv.THRESH_BINARY)
    edges_bin = np.where(edges_bin == 255, 1, 0)
    edges_skel = pcv.morphology.skeletonize(edges_bin)
    contours, hierarchy = cv.findContours(edges_skel.astype(np.uint8), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    edge_contours = [c for c in contours if cv.arcLength(c, False) > 100]
    measurement = max([cv.arcLength(c, False) / 2 * 0.052 for c in edge_contours], default=0)
    return measurement


def detected_edges(img_cv):
    # Convert to grayscale and apply edge detection
    img_gray = cv.cvtColor(img_cv, cv.COLOR_BGR2GRAY)
    img_blur = cv.GaussianBlur(img_gray, (3, 3), 0)
    edges = cv.Canny(image=img_blur, threshold1=50, threshold2=100)
    edges = cv.dilate(edges, None, iterations=1)
    edges = cv.erode(edges, None, iterations=1)
    return edges


def detect_objects_on_frame(frame, model):
    # Convert OpenCV frame to PIL Image
    img = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))

    # Perform detection
    results = model.predict(img)
    result = results[0]
    output = []

    # Convert image into OpenCV format for processing
    opencv_img = np.array(img)
    if opencv_img.shape[2] == 4:
        opencv_img = cv.cvtColor(opencv_img, cv.COLOR_RGBA2BGR)

    # Iterate through detected objects
    for box in result.boxes:
        x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
        length = scratch_len(opencv_img, [x1, y1, x2, y2])
        class_id = box.cls[0].item()
        prob = round(box.conf[0].item(), 2)
        output.append([x1, y1, x2, y2, result.names[class_id], prob, round(length, 2)])

    return output


def show_frame_with_detections(original_frame, detections):
    frame = original_frame.copy()
    for det in detections:
        x1, y1, x2, y2, class_name, prob, length = det
        cv.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        label = f"{class_name}: {prob * 100:.2f}% Length: {length}"
        cv.putText(frame, label, (int(x1), int(y1) - 10), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)

    # cv.imshow('Real-time Detections', frame)
    # cv.waitKey(0)
    # cv.imshow('original', original_frame)
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    return frame


if __name__ == "__main__":
    original_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    detections = [
        (100, 100, 200, 200, "ObjectA", 0.95, 100),
        (300, 150, 400, 300, "ObjectB", 0.80, 150)
    ]

    show_frame_with_detections(original_frame, detections)
