import os

# --- ĐƯỜNG DẪN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'weights', 'yolov8n.pt') 

# --- CẤU HÌNH CLASS (COCO DATASET) ---
# YOLO mặc định: 2=Car, 5=Bus, 7=Truck
CLASS_ID_MAP = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

# --- CÀI ĐẶT HIỂN THỊ ---
DASHBOARD_HEIGHT = 200  # Tăng chiều cao lên để vẽ bảng to đẹp
VIDEO_WIDTH = 960
VIDEO_HEIGHT = 540

COLORS = {
    "text": (0, 0, 0),             # Chữ đen (cho nền trắng)
    "zone_fill": (0, 255, 0),      # Xanh lá mạ (như hình mẫu)
    "zone_line": (255, 255, 255),
    "bbox": (0, 255, 0),           # Box xanh
    "trace": (0, 200, 0),          # Vết đi màu xanh đậm
    "dashboard_bg": (255, 255, 255) # Nền bảng màu Trắng
}