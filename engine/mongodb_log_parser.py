# engine/mongodb_log_parser.py
import pandas as pd
import os
import sys
import json
import argparse
from datetime import datetime

# Thêm thư mục gốc để import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def parse_mongo_log_file(source_log_path, output_csv_path):
    """
    Đọc file log JSON của MongoDB và chuyển đổi thành định dạng CSV chuẩn hóa.
    """
    if not os.path.exists(source_log_path):
        print(f"Lỗi: File log nguồn của MongoDB không tồn tại tại '{source_log_path}'")
        return

    print(f"Đang phân tích log của MongoDB từ: {source_log_path}")
    
    parsed_records = []
    
    with open(source_log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                
                # Chỉ xử lý các dòng log ghi lại các câu lệnh (component: COMMAND)
                if log_entry.get("c") == "COMMAND":
                    timestamp = pd.to_datetime(log_entry.get("t", {}).get("$date"), utc=True)
                    attributes = log_entry.get("attr", {})
                    
                    # Trích xuất thông tin
                    # Lệnh query nằm trong nhiều key khác nhau tùy phiên bản Mongo
                    command_obj = attributes.get('command') or attributes.get('originatingCommand')
                    if not command_obj:
                        continue
                        
                    # Lấy tên lệnh (find, insert, update,...) và tên collection
                    command_type = next(iter(command_obj))
                    collection = command_obj.get(command_type)
                    
                    # Cố gắng lấy thông tin user và db
                    user = attributes.get('user', 'N/A')
                    db = command_obj.get('$db', 'N/A')
                    
                    # Lấy IP client từ remote address
                    client_ip = 'N/A'
                    if 'remote' in attributes and isinstance(attributes['remote'], str):
                         client_ip = attributes['remote'].split(':')[0]

                    # Tạo một "câu lệnh" giả lập để dễ đọc
                    pseudo_query = f"{command_type.upper()} on '{collection}' with filter: {json.dumps(command_obj.get('filter') or command_obj.get('q'))}"

                    parsed_records.append({
                        'timestamp': timestamp,
                        'user': user,
                        'client_ip': client_ip,
                        'database': db,
                        'query': pseudo_query
                    })

            except (json.JSONDecodeError, AttributeError, KeyError):
                # Bỏ qua các dòng không phải JSON hoặc không có cấu trúc mong muốn
                continue

    if not parsed_records:
        print("Không tìm thấy câu lệnh COMMAND nào trong file log của MongoDB.")
        return

    df_final = pd.DataFrame(parsed_records)
    
    output_dir = os.path.dirname(output_csv_path)
    os.makedirs(output_dir, exist_ok=True)
    
    df_final.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"Phân tích log MongoDB thành công. Đã ghi {len(df_final)} dòng vào '{output_csv_path}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phân tích log JSON của MongoDB.")
    parser.add_argument("--input", type=str, required=True, help="Đường dẫn đến file log của MongoDB.")
    parser.add_argument("--output", type=str, required=True, help="Đường dẫn đến file CSV đầu ra.")
    args = parser.parse_args()
    
    parse_mongo_log_file(args.input, args.output)