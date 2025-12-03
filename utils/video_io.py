import cv2
import os
import datetime
from tkinter import Tk, filedialog, messagebox

def select_source_video():
    """Mở cửa sổ chọn file video"""
    Tk().withdraw()
    video_path = filedialog.askopenfilename(
        title="Chọn video Input",
        filetypes=[("Video files", "*.mp4;*.avi;*.mkv")]
    )
    if not video_path:
        messagebox.showerror("Lỗi", "Bạn chưa chọn video!")
        return None
    return video_path

def select_output_folder():
    """Chọn thư mục lưu kết quả"""
    output_dir = filedialog.askdirectory(title="Chọn nơi lưu kết quả")
    return output_dir

def create_video_writer(cap, output_dir, input_path, dashboard_height=0):
    """Tạo VideoWriter (tự cộng thêm chiều cao dashboard)"""
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    filename = os.path.basename(input_path).split('.')[0]
    save_path = os.path.join(output_dir, f"{filename}_processed_{timestamp}.mp4")

    # Chiều cao output = Chiều cao video + Dashboard
    final_height = height + dashboard_height
    writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, final_height))
    
    return writer, save_path