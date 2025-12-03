import cv2
import numpy as np
from config import VIDEO_HEIGHT, VIDEO_WIDTH, DASHBOARD_HEIGHT
class ZoneDrawer:
    def __init__(self):
        self.polygons = []
        self.current_polygon = []
        # Cập nhật tiêu đề hướng dẫn
        self.window_name = "SETUP: Draw Zones (Enter: Save, U: Undo, Q: Finish)"

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_polygon.append((x, y))

    def run(self, video_path):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        
        if not ret: return []

        # Resize frame
        frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        while True:
            display = frame.copy()
            
            # 1. Vẽ các vùng đã lưu (Màu xanh lá)
            for i, poly in enumerate(self.polygons):
                pts = np.array(poly, np.int32)
                cv2.polylines(display, [pts], True, (0, 255, 0), 2)
                cv2.putText(display, f"Zone {i+1}", poly[0], cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # 2. Vẽ vùng đang vẽ dở (Màu vàng)
            if self.current_polygon:
                pts_current = np.array(self.current_polygon, np.int32)
                cv2.polylines(display, [pts_current], False, (0, 255, 255), 2)
                for pt in self.current_polygon:
                    cv2.circle(display, pt, 4, (0, 0, 255), -1)

            cv2.imshow(self.window_name, display)
            key = cv2.waitKey(1) & 0xFF

            # --- XỬ LÝ PHÍM BẤM ---
            if key == 13: # Enter: Lưu vùng
                if len(self.current_polygon) > 2:
                    self.polygons.append(self.current_polygon)
                    self.current_polygon = []
                    print(f"--> Saved Zone {len(self.polygons)}")
            
            elif key == ord('u'): # U: Undo
                if len(self.current_polygon) > 0:
                    # Trường hợp 1: Đang vẽ dở -> Xóa điểm cuối cùng
                    removed = self.current_polygon.pop()
                    print(f"Removed point: {removed}")
                elif len(self.polygons) > 0:
                    # Trường hợp 2: Không vẽ gì -> Xóa vùng vừa lưu gần nhất (nếu muốn)
                    self.polygons.pop()
                    print(f"Removed last saved Zone. Remaining: {len(self.polygons)}")

            elif key == ord('q'): # Q: Quit
                break
        
        cv2.destroyWindow(self.window_name)
        return self.polygons