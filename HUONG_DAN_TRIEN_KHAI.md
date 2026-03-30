# Hướng dẫn Triển khai Hệ thống VRP với Docker

Tài liệu này hướng dẫn bạn cách triển khai hệ thống VRP Logistics bằng Docker. Việc sử dụng Docker giúp bạn giải quyết vấn đề "quá nhiều file" bằng cách đóng gói toàn bộ ứng dụng thành các container dễ quản lý.

## 1. Tại sao dùng Docker lại giải quyết vấn đề "quá nhiều file"?

Khi bạn triển khai thủ công, bạn phải copy hàng ngàn file (`node_modules`, các file mã nguồn, môi trường ảo Python...). Với Docker:
- **Đóng gói**: Tất cả mã nguồn và thư viện được nén vào các "Image".
- **Nhẹ nhàng**: Bạn chỉ cần cài đặt Docker trên máy chủ, sau đó chạy lệnh để tải và chạy các Image này.
- **Nhất quán**: Chạy trên máy bạn thế nào thì trên máy chủ sẽ chạy y hệt như vậy.

## 2. Các bước triển khai

### Bước 1: Chuẩn bị môi trường
Đảm bảo máy của bạn đã cài đặt:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (cho Windows/Mac) hoặc Docker Engine (cho Linux).

### Bước 2: Xây dựng và Khởi chạy
Mở terminal (PowerShell hoặc CMD) tại thư mục gốc của dự án và chạy lệnh sau:

```bash
docker-compose up --build -d
```

**Giải thích lệnh:**
- `--build`: Xây dựng lại các image từ mã nguồn mới nhất.
- `-d`: Chạy ở chế độ nền (detached mode).

### Bước 3: Kiểm tra trạng thái
Kiểm tra xem các container đã chạy ổn định chưa:

```bash
docker-compose ps
```

Xem log nếu có lỗi:

```bash
docker-compose logs -f
```

## 3. Truy cập ứng dụng

Sau khi khởi chạy thành công, bạn có thể truy cập:
- **Giao diện người dùng (Frontend)**: [http://localhost](http://localhost)
- **Hệ quản trị API (Backend Admin)**: [http://localhost/api/admin/](http://localhost/api/admin/)
- **Tài liệu API**: [http://localhost/api/docs/](http://localhost/api/docs/)

## 4. Các lệnh hữu ích khác

- **Dừng hệ thống**: `docker-compose down`
- **Xem log của backend**: `docker-compose logs -f backend`
- **Truy cập vào shell của backend**: `docker-compose exec backend sh`
- **Tạo tài khoản admin mới**: 
  ```bash
  docker-compose exec backend python manage.py createsuperuser
  ```

---
*Lưu ý: Trong môi trường thực tế (production), hãy nhớ đổi các biến môi trường trong file `docker-compose.yml` (như SECRET_KEY, DB_PASSWORD) để đảm bảo bảo mật.*

## 5. Triển khai lên Koyeb (Cloud Hosting)

Koyeb là một nền tảng tuyệt vời để chạy các ứng dụng Docker. Dưới đây là các bước để đưa sản phẩm của bạn lên Koyeb:

### Bước 1: Tạo tài khoản và App
1. Truy cập [Koyeb.com](https://www.koyeb.com/) và tạo tài khoản.
2. Nhấn **"Create App"**.

### Bước 2: Tạo Database (Postgres)
1. Trong bảng điều khiển Koyeb, chọn **"Databases"** -> **"Create Database"**.
2. Chọn **Postgres version 15**, vùng (Region) gần nhất (ví dụ: **Singapore - SIN**).
3. Đặt tên database là `vrp-db`.
4. Sau khi tạo xong, bạn sẽ thấy một chuỗi kết nối (Connection String/URI) bắt đầu bằng `postgres://...`. **Hãy lưu lại chuỗi này.**

### Bước 3: Triển khai Web Service
1. Quay lại trang App của bạn, nhấn **"Create Service"**.
2. Chọn **GitHub** và kết nối kho lưu trữ (repository) của bạn.
3. Trong phần **Builder**, chọn **"Docker"**.
4. Trong phần **Environment Variables**, thêm các biến sau:
   - `DATABASE_URL`: (Dán chuỗi kết nối của Postgres bạn vừa tạo ở Bước 2).
   - `PORT`: `10000`
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*` (hoặc tên miền của bạn trên Koyeb).
   - `SECRET_KEY`: (Một chuỗi ký tự ngẫu nhiên dài).
5. Trong phần **Exposed Ports**, đảm bảo port là `10000` (đúng với biến `PORT` ở trên).
6. Nhấn **"Deploy"**.

### Bước 4: Kiểm tra kết quả
Koyeb sẽ tự động xây dựng (build) Image từ Dockerfile và chạy ứng dụng. Sau vài phút, bạn sẽ có một URL công khai (ví dụ: `your-app-name.koyeb.app`) để truy cập vào hệ thống.
