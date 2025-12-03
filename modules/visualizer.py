import cv2
import numpy as np
from collections import defaultdict
from config import DASHBOARD_HEIGHT, COLORS, CLASS_ID_MAP

class Visualizer:
    def __init__(self, zones_polys):
        self.zones_polys = zones_polys
        # Lưu vết đường đi để vẽ: {track_id: [(x,y), (x,y), ...]}
        self.track_points = defaultdict(lambda: []) 

    def draw_scene(self, frame, detections, fps, zone_status, flow_counts):
        annotated_frame = frame.copy()
        
        # --- 1. VẼ VÙNG (Zones) ---
        overlay = annotated_frame.copy()
        for i, poly in enumerate(self.zones_polys):
            pts = np.array(poly, np.int32)
            # Màu xanh lá mạ, trong suốt
            cv2.fillPoly(overlay, [pts], COLORS["zone_fill"])
            cv2.polylines(annotated_frame, [pts], True, COLORS["zone_line"], 2)
            # Tên vùng: A, B, C...
            label = chr(65 + i) # 0->A, 1->B, 2->C
            cv2.putText(annotated_frame, label, tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)
        
        cv2.addWeighted(overlay, 0.4, annotated_frame, 0.6, 0, annotated_frame)

        # --- 2. VẼ XE & VẾT DI CHUYỂN (TRACE) ---
        for xyxy, track_id, class_id in zip(detections.xyxy, detections.tracker_id, detections.class_id):
            x1, y1, x2, y2 = map(int, xyxy)
            center = (int((x1+x2)/2), int(y2))
            class_name = CLASS_ID_MAP.get(class_id, "Other")

            # Cập nhật vết trace
            self.track_points[track_id].append(center)
            if len(self.track_points[track_id]) > 30: # Giới hạn độ dài vết
                self.track_points[track_id].pop(0)

            # Vẽ đường trace màu xanh
            points = np.array(self.track_points[track_id], dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated_frame, [points], False, COLORS["trace"], 2)
            cv2.circle(annotated_frame, center, 4, (0, 0, 255), -1)

            # Vẽ Box & Label (Ví dụ: 12-Car)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), COLORS["bbox"], 2)
            cv2.putText(annotated_frame, f"{track_id}-{class_name}", (x1, y1-8), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # --- 3. VẼ DASHBOARD (BẢNG TRẮNG) ---
        dashboard = self._create_white_dashboard(frame.shape[1], fps, zone_status, flow_counts)
        
        # Ghép ảnh
        final_frame = np.vstack([annotated_frame, dashboard])
        return final_frame

    def _create_white_dashboard(self, width, fps, zone_status, flow_counts):
        # Tạo nền trắng
        board = np.ones((DASHBOARD_HEIGHT, width, 3), dtype=np.uint8) * 255
        
        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        black = (0, 0, 0)
        red = (0, 0, 255)
        blue = (255, 0, 0)

        # --- BẢNG 1: TRẠNG THÁI VÙNG (BÊN TRÁI) ---
        # Header: Vehicle | Zone A | Zone B | Zone C ...
        cv2.putText(board, "Vehicle", (20, 30), font, 0.7, black, 2)
        start_x = 150
        col_width = 100
        
        # Vẽ Header Zones
        for i in range(len(self.zones_polys)):
            label = f"Pos {chr(65+i)}" # Pos A, Pos B...
            cv2.putText(board, label, (start_x + i*col_width, 30), font, 0.7, black, 2)
            
        # Vẽ Dữ liệu (Rows: Car, Truck, Bus)
        y_offset = 70
        total_counts = [0] * len(self.zones_polys)
        
        for cls_name in ["Car", "Truck", "Bus"]:
            # Cột tên xe (Màu đỏ như hình)
            cv2.putText(board, cls_name, (20, y_offset), font, 0.7, red, 2)
            
            # Cột số liệu
            counts = zone_status.get(cls_name, [0]*len(self.zones_polys))
            for i, count in enumerate(counts):
                cv2.putText(board, str(count), (start_x + i*col_width + 10, y_offset), font, 0.7, blue, 2)
                total_counts[i] += count
            
            # Kẻ dòng kẻ ngang mờ
            cv2.line(board, (10, y_offset + 10), (start_x + len(self.zones_polys)*col_width, y_offset + 10), (200,200,200), 1)
            y_offset += 40

        # --- BẢNG 2: TRAJECTORY (BÊN PHẢI) ---
        # Vẽ đường ngăn cách dọc
        mid_x = start_x + len(self.zones_polys)*col_width + 50
        cv2.line(board, (mid_x, 10), (mid_x, DASHBOARD_HEIGHT-10), black, 2)

        # Header Trajectory
        cv2.putText(board, "Trajectory", (mid_x + 20, 30), font, 0.7, black, 2)
        cv2.putText(board, "Count", (mid_x + 200, 30), font, 0.7, black, 2)

        # Liệt kê các luồng (A -> B, A -> C...)
        traj_y = 70
        for cls_name in ["Car", "Truck"]: # Chỉ hiện Car/Truck cho đỡ rối
            flows = flow_counts[cls_name]
            for (start, end), count in flows.items():
                label = f"{chr(65+start)} - {chr(65+end)} ({cls_name})" # VD: A - B (Car)
                cv2.putText(board, label, (mid_x + 20, traj_y), font, 0.6, blue, 2)
                cv2.putText(board, str(count), (mid_x + 200, traj_y), font, 0.6, red, 2)
                traj_y += 30
                if traj_y > DASHBOARD_HEIGHT - 10: break

        # Hiện FPS góc phải dưới
        cv2.putText(board, f"FPS: {fps:.1f}", (width - 150, DASHBOARD_HEIGHT - 20), font, 0.6, (0, 100, 0), 2)

        return board