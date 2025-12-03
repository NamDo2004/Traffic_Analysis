from ultralytics import YOLO
import supervision as sv
import torch

class VehicleDetector:
    def __init__(self, model_path):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading Model on: {device}")
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()

    def detect_and_track(self, frame):
        # 1. Detect
        results = self.model(frame, verbose=False, conf=0.5)[0]
        
        # 2. Convert sang Supervision Format
        detections = sv.Detections.from_ultralytics(results)
        
        # 3. Tracking (Gán ID)
        tracked_detections = self.tracker.update_with_detections(detections)
        return tracked_detections