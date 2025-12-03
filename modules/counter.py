from shapely.geometry import Point, Polygon
from collections import defaultdict
from config import CLASS_ID_MAP

class TrafficCounter:
    def __init__(self, zones_polygons):
        self.zones = [Polygon(p) for p in zones_polygons]
        
        # Lưu lịch sử vùng: {track_id: [Zone_Index_History]}
        self.vehicle_history = defaultdict(list)
        
        # Đếm chi tiết: self.counts[class_name][zone_index]
        # Ví dụ: self.counts["Car"][0] = 5 (Có 5 xe con ở Zone 1)
        self.zone_counts = {name: defaultdict(int) for name in CLASS_ID_MAP.values()}
        self.zone_counts["Other"] = defaultdict(int)

        # Đếm luồng A -> B: self.flow_counts[class_name][(Start, End)]
        self.flow_counts = {name: defaultdict(int) for name in CLASS_ID_MAP.values()}
        self.flow_counts["Other"] = defaultdict(int)

    def update(self, detections):
        # Reset đếm xe hiện tại trong vùng (snapshot)
        current_zone_status = {name: [0]*len(self.zones) for name in self.zone_counts.keys()}

        for xyxy, track_id, class_id in zip(detections.xyxy, detections.tracker_id, detections.class_id):
            x1, y1, x2, y2 = map(int, xyxy)
            center = Point((x1+x2)/2, y2)
            
            # Lấy tên loại xe
            class_name = CLASS_ID_MAP.get(class_id, "Other")

            # 1. Check xe đang ở vùng nào
            current_zone_idx = -1
            for i, zone in enumerate(self.zones):
                if zone.contains(center):
                    current_zone_idx = i
                    current_zone_status[class_name][i] += 1 # Đếm xe đang đỗ/chạy trong vùng
                    break
            
            # 2. Logic Luồng A -> B (Trajectory Counting)
            if current_zone_idx != -1:
                history = self.vehicle_history[track_id]
                
                # Nếu mới vào vùng khác vùng trước đó
                if not history or history[-1] != current_zone_idx:
                    if history: 
                        prev_zone = history[-1]
                        # Cộng luồng: A -> B cho loại xe này
                        self.flow_counts[class_name][(prev_zone, current_zone_idx)] += 1
                    
                    self.vehicle_history[track_id].append(current_zone_idx)

        return current_zone_status, self.flow_counts