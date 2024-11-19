from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('yolov8m-seg.yaml').load('yolov8m-seg.pt')
    results = model.train(data=r'\\puffball.labs.eait.uq.edu.au\s4764481\Desktop\s-seg\dataset\data.yaml', epochs=300, batch=-1, imgsz=1280)