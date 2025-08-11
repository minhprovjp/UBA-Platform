# backend_api/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- Schema cơ bản cho Anomaly ---
# Chứa các trường chung mà cả khi tạo mới và khi đọc đều cần đến.
class AnomalyBase(BaseModel):
    timestamp: datetime
    user: str
    client_ip: Optional[str] = None
    database: Optional[str] = None
    query: str
    anomaly_type: str
    score: Optional[float] = None
    reason: Optional[str] = None
    status: str

# --- Schema để trả về cho người dùng ---
# Kế thừa từ AnomalyBase và thêm các trường chỉ có sau khi đã được lưu vào CSDL (như id).
class Anomaly(AnomalyBase):
    id: int

    # Cấu hình này rất quan trọng: nó bảo Pydantic hãy đọc dữ liệu
    # từ các thuộc tính của một đối tượng SQLAlchemy (chế độ ORM).
    class Config:
        from_attributes = True # Dành cho Pydantic v2. Nếu dùng Pydantic v1, hãy dùng `orm_mode = True`