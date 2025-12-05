import os
import shutil
from ultralytics import YOLO


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, 'yolo12s.pt') 

output_folder_name = 'yolov12s_openvino'
target_folder = os.path.join(BASE_DIR, output_folder_name)

print(f"1. Đường dẫn file gốc: {model_path}")
print(f"2. Đường dẫn sẽ lưu: {target_folder}")

# Kiểm tra xem file gốc có tồn tại không
if not os.path.exists(model_path):
    print(f"❌ LỖI: Không tìm thấy file {model_path}")
    exit()

model = YOLO(model_path)

print("⏳ Đang export sang OpenVINO (FP16)...")
exported_path = model.export(format='openvino', half=True) 

# Lấy đường dẫn folder mặc định mà YOLO vừa tạo ra
# exported_path trả về file metadata lấy folder cha
default_created_folder = os.path.dirname(exported_path)

# Đổi tên/Di chuyển về folder mong muốn
try:
    # Nếu folder mặc định khác tên folder mình muốn thì mới xử lý
    if default_created_folder != target_folder:
        # Nếu folder đích đã tồn tại, xóa nó đi để ghi mới
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
            print(f"   -> Đã xóa folder cũ: {output_folder_name}")
        
        # Đổi tên folder mặc định thành tên mình muốn
        os.rename(default_created_folder, target_folder)
        
    print(f"✅ THÀNH CÔNG! Model đã được lưu tại:\n   {target_folder}")

except Exception as e:
    print(f"❌ Có lỗi khi di chuyển folder: {e}")