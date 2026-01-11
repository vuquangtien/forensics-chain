# 📜 FORENSIC-CHAIN

## Hệ thống Quản lý Chuỗi Hành trình Chứng cứ Số dựa trên Blockchain

Forensic-Chain là hệ thống đảm bảo tính toàn vẹn và khả năng truy vết của bằng chứng số trong quá trình điều tra, truy tố và xét xử.

---

## 📋 Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Cài đặt](#3-cài-đặt)
4. [Hướng dẫn sử dụng](#4-hướng-dẫn-sử-dụng)
5. [API Reference](#5-api-reference)
6. [Ví dụ code](#6-ví-dụ-code)

---

## 1. Tổng quan

### 1.1 Mục đích
- **Bảo toàn tính toàn vẹn**: Mọi bằng chứng được ghi lại với mã băm SHA256, không thể thay đổi
- **Truy vết hoàn toàn**: Theo dõi chuỗi hành trình bằng chứng từ thu thập → giám định → truy tố → xét xử
- **Minh bạch & kiểm toán**: Mọi giao dịch được ghi nhận trên blockchain, có thể kiểm tra bất kỳ lúc nào

### 1.2 Các vai trò trong hệ thống
| Vai trò | Mô tả |
|---------|-------|
| `investigator` | Điều tra viên - Thu thập bằng chứng |
| `forensic_expert` | Chuyên gia pháp y - Giám định kỹ thuật |
| `prosecutor` | Công tố viên - Sử dụng cho truy tố |
| `judge` | Thẩm phán - Xem xét tại tòa |
| `admin` | Quản trị viên - Quản lý hệ thống |

### 1.3 4 Chức năng chính (Smart Contract)
1. **Tạo bằng chứng** (Create) - Ghi nhận bằng chứng mới vào blockchain
2. **Chuyển giao** (Transfer) - Chuyển quyền sở hữu giữa các bên
3. **Xóa bằng chứng** (Delete) - Vô hiệu hóa (lịch sử vẫn bảo toàn)
4. **Hiển thị** (Display) - Truy vấn thông tin và lịch sử

---

## 2. Kiến trúc hệ thống

### 2.1 Sơ đồ kiến trúc

```
┌─────────────────────────────────────────────────────────────────┐
│                        FORENSIC-CHAIN                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Điều tra viên │    │ Chuyên gia   │    │  Công tố /   │      │
│  │              │    │   Pháp y     │    │   Thẩm phán  │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    REST API (Flask)                       │  │
│  │   /api/participants  /api/evidence  /api/blockchain       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   SMART CONTRACT                          │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐ │  │
│  │  │   Create   │ │  Transfer  │ │   Delete   │ │ Display│ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐               │
│         ▼                   ▼                   ▼               │
│  ┌────────────┐    ┌──────────────┐    ┌──────────────┐        │
│  │  Evidence  │    │  Participant │    │  Blockchain  │        │
│  │  Registry  │    │   Registry   │    │    (PoW)     │        │
│  └────────────┘    └──────────────┘    └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

                              │
                              ▼
              ┌──────────────────────────────┐
              │  Distributed Evidence Store  │
              │    (Lưu trữ file gốc)        │
              │    - Chỉ lưu hash trên BC    │
              └──────────────────────────────┘
```

### 2.2 Cấu trúc thư mục

```
forensic-chain/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── blockchain.py        # Blockchain core (Block, Chain)
│   ├── models.py            # Data models (Evidence, Participant)
│   └── smart_contract.py    # Business logic (4 chức năng chính)
├── api/
│   └── app.py               # REST API endpoints
├── tests/
│   └── test_system.py       # Test script
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

### 2.3 Các module chính

| Module | File | Mô tả |
|--------|------|-------|
| **Blockchain** | `src/blockchain.py` | Triển khai chuỗi khối với Proof of Work |
| **Models** | `src/models.py` | Định nghĩa Evidence, Participant, TransferRecord |
| **Smart Contract** | `src/smart_contract.py` | Logic nghiệp vụ chính |
| **REST API** | `api/app.py` | HTTP endpoints cho tương tác |

### 2.4 Luồng dữ liệu

```
1. TẠO BẰNG CHỨNG:
   File gốc → SHA256 Hash → Evidence Registry + Blockchain

2. CHUYỂN GIAO:
   Kiểm tra quyền → Cập nhật owner → Ghi lịch sử → Blockchain

3. XÁC MINH:
   Hash file hiện tại ←→ Hash trên blockchain → Kết quả
```

---

## 3. Cài đặt

### 3.1 Yêu cầu
- Python 3.8+
- pip

### 3.2 Cài đặt

```bash
# Clone repository
cd forensic-chain

# Tạo môi trường ảo
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3.3 Kiểm tra cài đặt

```bash
python tests/test_system.py
```

---

## 4. Hướng dẫn sử dụng

### 4.1 Sử dụng trực tiếp (Python)

```python
from src.smart_contract import ForensicContract
import hashlib

# Khởi tạo
contract = ForensicContract()

# 1. Đăng ký người tham gia
contract.register_participant(
    participant_id="INV001",
    name="Nguyễn Văn A",
    role="investigator",
    organization="Công an TP.HCM"
)

# 2. Tạo bằng chứng
file_content = open("evidence.jpg", "rb").read()
file_hash = hashlib.sha256(file_content).hexdigest()

contract.create_evidence(
    evidence_id=file_hash[:16],
    description="Ảnh hiện trường vụ án",
    creator_id="INV001",
    file_hash=file_hash,
    file_location="/evidence_store/001.jpg",
    case_id="CASE-2026-001"
)

# 3. Chuyển giao
contract.transfer_evidence(
    evidence_id=file_hash[:16],
    from_owner_id="INV001",
    to_owner_id="FOR001",
    reason="Chuyển để giám định"
)

# 4. Xác minh tính toàn vẹn
contract.verify_evidence_integrity(file_hash[:16], file_hash)
```

### 4.2 Sử dụng qua REST API

**Khởi động server:**
```bash
python api/app.py
```

Server chạy tại: `http://localhost:5000`

**Các endpoint chính:**

```bash
# Đăng ký người tham gia
curl -X POST http://localhost:5000/api/participants \
  -H "Content-Type: application/json" \
  -d '{
    "participant_id": "INV001",
    "name": "Nguyễn Văn A",
    "role": "investigator",
    "organization": "Công an TP.HCM"
  }'

# Tạo bằng chứng
curl -X POST http://localhost:5000/api/evidence \
  -H "Content-Type: application/json" \
  -d '{
    "evidence_id": "abc123",
    "description": "Video giám sát",
    "creator_id": "INV001",
    "file_hash": "sha256_hash_here",
    "file_location": "/store/video.mp4",
    "case_id": "CASE-2026-001"
  }'

# Chuyển giao
curl -X POST http://localhost:5000/api/evidence/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "evidence_id": "abc123",
    "from_owner_id": "INV001",
    "to_owner_id": "FOR001",
    "reason": "Giám định kỹ thuật"
  }'

# Xem lịch sử
curl http://localhost:5000/api/evidence/abc123/history

# Xác minh blockchain
curl http://localhost:5000/api/blockchain/verify
```

---

## 5. API Reference

### 5.1 Participants

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/participants` | Đăng ký người tham gia |
| GET | `/api/participants` | Liệt kê tất cả |
| GET | `/api/participants/{id}` | Lấy thông tin |

### 5.2 Evidence

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/evidence` | Tạo bằng chứng mới |
| GET | `/api/evidence` | Liệt kê tất cả |
| GET | `/api/evidence/{id}` | Lấy chi tiết |
| DELETE | `/api/evidence/{id}` | Xóa (vô hiệu hóa) |
| POST | `/api/evidence/transfer` | Chuyển giao |
| GET | `/api/evidence/{id}/history` | Xem lịch sử |
| POST | `/api/evidence/{id}/verify` | Xác minh tính toàn vẹn |

### 5.3 Blockchain

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/blockchain` | Xem toàn bộ blockchain |
| GET | `/api/blockchain/info` | Thông tin tổng quan |
| GET | `/api/blockchain/verify` | Kiểm tra tính hợp lệ |

### 5.4 Utility

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/health` | Kiểm tra trạng thái hệ thống |
| POST | `/api/hash` | Tính SHA256 hash |

---

## 6. Ví dụ code

### 6.1 Quy trình điều tra hoàn chỉnh

```python
from src.smart_contract import ForensicContract
import hashlib

# Khởi tạo hệ thống
contract = ForensicContract()

# === BƯỚC 1: Đăng ký các bên tham gia ===
contract.register_participant("INV001", "Điều tra viên An", "investigator", "CA TP.HCM")
contract.register_participant("FOR001", "Chuyên gia Bình", "forensic_expert", "Viện KHHS")
contract.register_participant("PRO001", "Công tố viên Cường", "prosecutor", "VKS TP.HCM")
contract.register_participant("JUD001", "Thẩm phán Dung", "judge", "TAND TP.HCM")

# === BƯỚC 2: Thu thập và đăng ký bằng chứng ===
# Giả lập file bằng chứng
video_content = b"Video surveillance footage of crime scene"
video_hash = hashlib.sha256(video_content).hexdigest()

success, msg = contract.create_evidence(
    evidence_id=video_hash[:16],
    description="Video camera giám sát khu vực xảy ra vụ án, ghi lại lúc 23:45 ngày 01/01/2026",
    creator_id="INV001",
    file_hash=video_hash,
    file_location="/evidence_store/case_001/video_001.mp4",
    case_id="CASE-2026-001",
    metadata={
        "type": "video",
        "duration": "00:15:30",
        "resolution": "1920x1080",
        "source": "Camera #3 - Ngã tư XYZ"
    }
)
print(f"Tạo bằng chứng: {msg}")

# === BƯỚC 3: Chuyển giao theo quy trình ===
# Điều tra viên → Chuyên gia pháp y
contract.transfer_evidence(
    video_hash[:16], "INV001", "FOR001",
    "Chuyển để phân tích và giám định video"
)

# Chuyên gia pháp y → Công tố viên
contract.transfer_evidence(
    video_hash[:16], "FOR001", "PRO001",
    "Hoàn thành giám định, chuyển hồ sơ truy tố"
)

# Công tố viên → Thẩm phán
contract.transfer_evidence(
    video_hash[:16], "PRO001", "JUD001",
    "Nộp bằng chứng cho phiên tòa ngày 15/03/2026"
)

# === BƯỚC 4: Xem lịch sử chuỗi hành trình ===
evidence = contract.get_evidence(video_hash[:16])
print("\n=== LỊCH SỬ CHUỖI HÀNH TRÌNH ===")
for i, t in enumerate(evidence['transfer_history'], 1):
    print(f"{i}. {t['from_owner']} → {t['to_owner']}")
    print(f"   Lý do: {t['reason']}")
    print(f"   Thời gian: {t['timestamp']}")

# === BƯỚC 5: Xác minh tính toàn vẹn ===
# File không thay đổi
is_valid, msg = contract.verify_evidence_integrity(video_hash[:16], video_hash)
print(f"\nXác minh file gốc: {msg}")

# File bị thay đổi
tampered_hash = hashlib.sha256(b"Modified content").hexdigest()
is_valid, msg = contract.verify_evidence_integrity(video_hash[:16], tampered_hash)
print(f"Xác minh file bị sửa: {msg}")

# === BƯỚC 6: Kiểm tra blockchain ===
info = contract.get_blockchain_info()
print(f"\nBlockchain: {info['total_blocks']} khối, hợp lệ: {info['is_valid']}")
```

---

## 📞 Liên hệ

Nếu có câu hỏi hoặc góp ý, vui lòng tạo issue trên repository.

---

**© 2026 Forensic-Chain Project**
