# backend/configs/config_loader.py
import json
import os


#CONFIG_DIR = os.path.join(os.getcwd(), "configs")
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "") 

# chỗ này là ID của mấy page và file config tương ứng
PAGE_MAP = {
    "105524314620167": "bo_thuoc_360.json",
    "2002": "bds_luxury.json"
}

def load_config(page_id):
    """
    Hàm đọc file config JSON dựa trên Page ID
    """
    filename = PAGE_MAP.get(str(page_id))
    
    if not filename:
        print(f" Không tìm thấy mapping cho Page ID: {page_id}")
        return None

    file_path = os.path.join(CONFIG_DIR, filename)
    
    if not os.path.exists(file_path):
        print(f" File không tồn tại: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        page_name = config.get("page_name")
        if not page_name:
            page_name = config.get("meta_data", {}).get("brand_default", "Unknown Page")
        return config
        
    except Exception as e:
        print(f" Lỗi đọc config {filename}: {e}")
        return None