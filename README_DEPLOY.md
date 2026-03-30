# Tài liệu triển khai hệ thống VRP Logistics

Hệ thống quản lý vận tải và tối ưu lộ trình sử dụng thuật toán Bin Packing + OR-Tools.

## 1. Yêu cầu hệ thống (System Requirements)
- **Hệ điều hành**: Linux (Ubuntu 20.04+ khuyên dùng) hoặc Windows có hỗ trợ Docker.
- **RAM**: Tối thiểu 2GB (Để chạy các thuật toán tối ưu VRP của Google OR-Tools).
- **Bộ nhớ**: 5GB trống.

## 2. Yêu cầu phần mềm (Software Requirements)
### Backend (Python/Django)
- **Python**: 3.10+
- **Database**: PostgreSQL 15+
- **Thư viện chính**:
    - `Django 5.0`
    - `Google OR-Tools` (Tối ưu lộ trình)
    - `Gunicorn` (Production server)

### Frontend (React/Nginx)
- **Node.js**: 20.x
- **NPM**: 10.x
- **UI Framework**: `Ant Design 6`
- **Map**: `Leaflet & OpenStreetMap`

## 3. Hướng dẫn triển khai nhanh (Quick Start)
Đảm bảo máy đã cài **Docker** và **Docker Compose**.

1. **Clone dự án**:
   ```bash
   git clone <repository_url>
   cd vrp_duphong
   ```

2. **Khởi chạy bằng Docker**:
   ```bash
   docker-compose up --build -d
   ```

3. **Truy cập**:
   - Web App: [http://localhost](http://localhost)
   - API Docs: [http://localhost/api/](http://localhost/api/)

---
*Lưu ý: Bạn có thể cấu hình thông tin Database và Secret Key trong file `docker-compose.yml` trước khi chạy.*
