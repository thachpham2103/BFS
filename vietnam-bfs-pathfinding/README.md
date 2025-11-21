# VietNam-BFS-PATHFINDING - Tìm đường đi giữa các tỉnh thành Việt Nam

## Mô tả dự án

Dự án này áp dụng thuật toán **BFS (Breadth-First Search)** để tìm đường đi ngắn nhất giữa 2 tỉnh thành bất kỳ ở Việt Nam. Dự án sử dụng dữ liệu từ [vietnamese-provinces-database](../vietnamese-provinces-database) để xây dựng đồ thị các tỉnh thành lân cận và tính toán lộ trình di chuyển.


## Tính năng

- 🗺️ **Pathfinding:** Tìm đường đi ngắn nhất giữa 2 tỉnh (BFS algorithm, <1ms)
- 🔍 **Fuzzy Search:** Tìm kiếm tỉnh không cần dấu (ví dụ: "ha noi" → Hà Nội)
- 📊 **Province Info:** Thông tin chi tiết về tỉnh và các tỉnh lân cận
- 🌐 **REST API:** FastAPI với Swagger UI documentation
- ⚡ **High Performance:** Average pathfinding time <1ms, API response <50ms
- 🎯 **34 Provinces:** Hỗ trợ 34 tỉnh thành Việt Nam (sau sáp nhập hành chính)

## Thuật toán BFS

**BFS (Breadth-First Search)** là thuật toán duyệt đồ thị theo chiều rộng, phù hợp để tìm đường đi ngắn nhất trong đồ thị không trọng số. Thuật toán hoạt động bằng cách:

1. Bắt đầu từ tỉnh xuất phát
2. Duyệt lần lượt các tỉnh lân cận (cách 1 bước)
3. Tiếp tục duyệt các tỉnh lân cận của các tỉnh vừa duyệt (cách 2 bước)
4. Lặp lại cho đến khi tìm thấy tỉnh đích

## Cấu trúc dữ liệu

Dự án sử dụng dữ liệu từ `vietnamese-provinces-database` bao gồm:
- Danh sách 34 tỉnh thành Việt Nam (sau sap nhap)
- Thông tin các tỉnh giáp ranh (tỉnh lân cận)
- Dữ liệu đơn vị hành chính

## Yêu cầu hệ thống

- Python 3.8+ (khuyến nghị Python 3.11)
- Các thư viện: FastAPI, Pydantic, Uvicorn (xem `requirements.txt`)

## 📡 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/health` | Kiểm tra trạng thái hệ thống |
| `GET` | `/docs` | Swagger UI Documentation |
| `POST` | `/api/v1/path/find` | Tìm đường đi ngắn nhất |
| `POST` | `/api/v1/path/reachable` | Tìm các tỉnh có thể đến được |
| `POST` | `/api/v1/path/connectivity` | Kiểm tra kết nối 2 tỉnh |
| `GET` | `/api/v1/provinces` | Danh sách tất cả tỉnh |
| `GET` | `/api/v1/provinces/{id}` | Thông tin chi tiết tỉnh |
| `POST` | `/api/v1/provinces/search` | Tìm kiếm tỉnh theo tên |
| `GET` | `/api/v1/statistics` | Thống kê hệ thống |


## Hướng Dẫn Chạy API

## Bước 1: Cài đặt Dependencies

```bash
# Cài đặt tất cả các thư viện cần thiết
pip install -r requirements.txt
```

## Bước 2: Khởi động API Server

```bash
python src/api/main.py
```

## Bước 3: Kiểm tra API đang chạy

Sau khi khởi động, API sẽ chạy tại: **http://localhost:8000**

### Kiểm tra Health Check
```bash
curl http://localhost:8000/health
```

### Ví dụ: Tìm đường đi bằng API

**Request:**
```bash
POST /api/v1/path/find
{
  "start": "Hà Nội",
  "end": "TP. Hồ Chí Minh",
  "fuzzy_match": true
}
```

**Response:**
```json
{
  "path": ["Hà Nội", "Phú Thọ", "Thanh Hóa", "...", "Hồ Chí Minh"],
  "path_codes": ["01", "25", "38", "...", "79"],
  "distance": 10,
  "start_province": {"code": "01", "name": "Hà Nội"},
  "end_province": {"code": "79", "name": "Hồ Chí Minh"},
  "execution_time_ms": 0.26,
  "timestamp": "2025-11-21T13:39:04"
}
```

## Ví dụ kết quả

```
🗺️  Đường đi từ Hà Nội đến Hồ Chí Minh
============================================================
 1. Hà Nội
 2. Phú Thọ
 3. Thanh Hóa
 4. Nghệ An
 5. Quảng Trị
 6. Huế
 7. Quảng Ngãi
 8. Gia Lai
 9. Lâm Đồng
10. Hồ Chí Minh
============================================================
Tổng số tỉnh: 10
Thời gian: 0.26ms
```


## 📊 Tiến độ triển khai

- **BƯỚC 1:** Environment Setup & Configuration
- **BƯỚC 2:** Adjacency Data Creation & DataLoader
- **BƯỚC 3:** Models & Data Structures (Province, PathResult, Exceptions)
- **BƯỚC 4:** BFS Algorithm Implementation (ProvinceGraph, BFSPathfinder)
- **BƯỚC 5:** Service Layer (PathfindingService với 15+ methods)
- **BƯỚC 6:** REST API với FastAPI (9+ endpoints, Swagger UI)
- **BƯỚC 7:** CLI Tool (TODO)
- **BƯỚC 8:** Testing (pytest, >85% coverage) (TODO)
- **BƯỚC 9:** Documentation & Code Quality (TODO)
- **BƯỚC 10:** Integration & Deployment (TODO)

## 🚀 Performance

- **API Startup:** ~0.5s
- **BFS Pathfinding:** <1ms (average 0.05ms)
- **API Response Time:** <50ms
- **Memory Usage:** ~30MB (34 provinces loaded)
- **Concurrent Requests:** Hỗ trợ multiple workers với Uvicorn


## 🛠️ Tech Stack

- **Language:** Python 3.11
- **Web Framework:** FastAPI 0.104.1
- **Validation:** Pydantic 2.5.0 (TODO)
- **ASGI Server:** Uvicorn 0.24.0 (TODO)
- **Testing:** pytest 7.4.3 (TODO)
- **Algorithm:** BFS (Breadth-First Search)
- **Data Structure:** Adjacency List Graph


## Tham khảo

- [vietnamese-provinces-database](https://github.com/thanglequoc/vietnamese-provinces-database) - Nguồn dữ liệu tỉnh thành Việt Nam
- [BFS Algorithm](https://en.wikipedia.org/wiki/Breadth-first_search) - Thuật toán BFS
