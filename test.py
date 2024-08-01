from ultralytics import YOLO
import cv2 as cv
import random
import numpy as np

model = YOLO('Models/detect.pt')

img_path = 'images/new/Unknown.jpeg'

img = cv.imread(img_path)

classes = list(model.names.values())
classes_ids = [classes.index(cls) for cls in classes]
scratch_id = classes.index('scratch')
stain_id = classes.index('stain')

scratch_count, stain_count = 0, 0

conf = 0.2

results = model(img, conf=conf)

colors = [random.choices(range(256), k=3) for _ in classes_ids]
# print("Results:", results)

for result in results:
    for mask, box in zip(result.masks.xy, result.boxes):
        defect_id = int(box.cls[0])
        if defect_id == scratch_id:
            scratch_count += 1
        elif defect_id == stain_id:
            stain_count += 1
        else:
            break

        # print(f"Mask: {mask}")
        # print(f"Mask shape: {mask.shape}")

        if mask.size == 0 or len(mask.shape) != 2 or mask.shape[1] != 2:
            print("Error: Mask points do not have the correct shape")
            continue

        points = np.int32(mask)
        # print(f"Points: {points}")
        # print(f"Points shape: {points.shape}")

        color_number = classes_ids.index(int(box.cls[0]))
        cv.fillPoly(img, [points], colors[color_number])

print(f'scratch: {scratch_count}, stain: {stain_count}')
cv.imshow('Image', img)
cv.waitKey()
