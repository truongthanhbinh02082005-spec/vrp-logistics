# Hướng dẫn từng bước triển khai lên Koyeb (VRP Logistics)

Tài liệu này cung cấp các bước cực kỳ chi tiết để bạn đưa sản phẩm của mình lên internet bằng Koyeb.

## Phần 1: Tạo Database (Lưu trữ dữ liệu)

Koyeb cung cấp Database Postgres miễn phí rất tốt. Đừng tự chạy Postgres trong Docker trên Koyeb vì dữ liệu sẽ bị mất khi khởi động lại.

1.  Truy cập [Koyeb Dashboard](https://app.koyeb.com/).
2.  Nhấn nút **Create Service** (hoặc vào tab **Databases**).
3.  Chọn **Database Content Provider**: **Managed Database**.
4.  Chọn **PostgreSQL**.
5.  **Cấu hình**:
    *   **Name**: `vrp-db`
    *   **Version**: `15`
    *   **Region**: `Singapore (SIN)` (Chọn vùng này để tốc độ từ Việt Nam nhanh nhất).
    *   **Instance Type**: `Free tier`
6.  Nhấn **Create Database**.
7.  **QUAN TRỌNG**: Sau khi tạo xong, bạn sẽ thấy mục **Connections**. Hãy chọn định dạng **URI** (ví dụ: `postgres://user:password@host:port/dbname`). 
    *   Copy chuỗi này lại. Nó sẽ có dạng: `postgres://koyeb-user:xyz...`
    *   Đây chính là giá trị cho biến `DATABASE_URL`.

---

## Phần 2: Triển khai Ứng dụng (Web Service)

Dự án của bạn là một file Docker duy nhất chứa cả Backend và Frontend.

1.  Từ Dashboard, nhấn **Create App**.
2.  **Deployment Method**: Chọn **GitHub**.
3.  **Repository**: Chọn repo chứa code của bạn (ví dụ: `truongthanhbinh02082005-spec/vrp-logistics`).
4.  **Builder**: Chọn **Docker**.
5.  **Service Settings**:
    *   **Instance Type**: `Nano` (hoặc cao hơn nếu bạn có gói trả phí).
    *   **Regions**: `Singapore (SIN)`.
6.  **Environment Variables (Biến môi trường)**: Nhấn **Add Variable** và thêm đủ các dòng sau:
    | Key | Value | Ghi chú |
    | :--- | :--- | :--- |
    | `DATABASE_URL` | (Dán chuỗi URI ở bước 7 Phần 1) | Kết nối DB |
    | `PORT` | `10000` | Port ứng dụng |
    | `DEBUG` | `False` | Tắt chế độ debug |
    | `ALLOWED_HOSTS` | `*` | Cho phép mọi domain |
    | `SECRET_KEY` | `Mật_Mã_Bảo_Mật_Của_Bạn_123456` | Chuỗi ký tự bất kỳ |

7.  **Exposed Ports**:
    *   **Port**: `10000`
    *   **Protocol**: `HTTP`
    *   **Path**: `/` (Mặc định)

8.  **Health Check (Kiểm tra sức khỏe)**:
    *   Mở phần **Advanced settings**.
    *   Tìm **Health Check**.
    *   **Type**: `HTTP`
    *   **Path**: `/api/auth/login/` (Hoặc đường dẫn nào đó trả về 200 OK).
    *   **Grace period**: `60` (Cho ứng dụng 60 giây để khởi động).

9.  **Deploy**: Nhấn nút **Deploy**.

---

## Phần 3: Kiểm tra và sử dụng

1.  Koyeb sẽ bắt đầu quá trình **Build**. Bạn có thể xem log để biết tiến độ.
2.  Khi trạng thái chuyển sang **Healthy**, bạn sẽ thấy một link (Public URL) ở trên cùng.
    *   Ví dụ: `https://vrp-logistics-xyz.koyeb.app/`
3.  Truy cập link đó để sử dụng sản phẩm.

### Lưu ý khi cập nhật code:
- Mỗi khi bạn `git push` lên GitHub, Koyeb sẽ tự động nhận diện và triển khai bản mới nhất cho bạn.

### Tạo tài khoản Admin (Nếu cần):
Nếu bạn cần tạo `superuser` để vào trang Web Admin:
1.  Sử dụng [Koyeb CLI](https://www.koyeb.com/docs/cli) trên máy tính của bạn.
2.  Chạy lệnh: `koyeb service exec vrp-app -- python manage.py createsuperuser`
