from ultralytics import YOLO
import cv2
import numpy as np

class Detector:
    def __init__(self, model_path="yolov8n.pt", conf=0.4, device='cpu'):
        self.model = YOLO(model_path)
        self.conf = conf
        self.device = device

    def detect(self, frame):
        """
        Detects people in a frame using YOLOv8.
        Returns: [(x1, y1, x2, y2, conf, cls), ...]
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model.predict(rgb, imgsz=640, conf=self.conf, verbose=False)
        dets = []

        r = results[0]
        boxes = r.boxes
        if boxes is None:
            return dets

        for box in boxes:
            cls = int(box.cls.cpu().numpy()[0])
            conf = float(box.conf.cpu().numpy()[0])
            # Keep only 'person' class (class ID 0)
            if cls != 0:
                continue
            xyxy = box.xyxy.cpu().numpy()[0]
            x1, y1, x2, y2 = [int(x) for x in xyxy]
            dets.append((x1, y1, x2, y2, conf, cls))
        return dets