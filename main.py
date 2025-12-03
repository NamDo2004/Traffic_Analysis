import cv2
import time
from config import MODEL_PATH, DASHBOARD_HEIGHT, VIDEO_WIDTH, VIDEO_HEIGHT
from utils.video_io import select_source_video, select_output_folder, create_video_writer
from modules.zone_drawer import ZoneDrawer
from modules.detector import VehicleDetector
from modules.counter import TrafficCounter
from modules.visualizer import Visualizer
import datetime
import os

def main():
    # 1. SETUP: Chọn File & Vẽ Vùng
    video_path = select_source_video()
    if not video_path: return

    print("Đang mở cửa sổ vẽ vùng...")
    drawer = ZoneDrawer()
    zones = drawer.run(video_path)
    if not zones:
        print("Bạn chưa vẽ vùng nào! Kết thúc.")
        return

    output_dir = select_output_folder()
    
    # 2. INIT MODULES
    detector = VehicleDetector(MODEL_PATH)
    counter = TrafficCounter(zones)
    visualizer = Visualizer(zones)

    # 3. VIDEO READER & WRITER
    cap = cv2.VideoCapture(video_path)

    final_height = VIDEO_HEIGHT + DASHBOARD_HEIGHT
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    filename = os.path.basename(video_path).split('.')[0]
    save_path = os.path.join(output_dir, f"{filename}_resized_{timestamp}.mp4")

    # Writer ghi theo kích thước resize
    writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (VIDEO_WIDTH, final_height))

    # 4. MAIN LOOP
    print("Bắt đầu xử lý...")
    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret: break

        # --- [QUAN TRỌNG] RESIZE FRAME TRƯỚC KHI XỬ LÝ ---
        # Phải resize về đúng kích thước lúc vẽ (trong config.py)
        # Nếu không resize, tọa độ vùng vẽ sẽ bị lệch hoàn toàn.
        frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))
        # ---------------------------------------------------

        # --- XỬ LÝ ---
        detections = detector.detect_and_track(frame)
        zone_status, flow_counts = counter.update(detections)

        # --- TÍNH FPS ---
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        # --- HIỂN THỊ ---
        final_frame = visualizer.draw_scene(frame, detections, fps, zone_status, flow_counts)

        # Show & Save
        cv2.imshow("Smart Traffic Analysis", final_frame)
        writer.write(final_frame)

        if cv2.waitKey(1) == ord('q'):
            break

    # 5. CLEANUP
    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    print(f"Xong! File lưu tại: {save_path}")

if __name__ == "__main__":
    main()