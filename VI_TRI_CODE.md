# DANH SÁCH VỊ TRÍ CÁC TÍNH NĂNG TRONG MÃ NGUỒN

Dưới đây là danh sách chi tiết vị trí các tính năng quan trọng trong code của hệ thống (file và số dòng):

## 1. Import bản đồ (Frontend sử dụng `react-leaflet`)
Hệ thống hiển thị bản đồ ở 3 màn hình chính thuộc thư mục `frontend/src/pages/`:
- **Routes.jsx**: 
  - Dòng 4 - 15: Import thư viện `react-leaflet`, `leaflet`.
  - Dòng 46 - 66: Cấu hình fix lỗi hiển thị icon marker mặc định của Leaflet.
  - Dòng 435 - 489: Render component `<MapContainer>` hiển thị bản đồ phân tuyến.
- **DriverDashboard.jsx** (App Tài xế): 
  - Dòng 12 - 33: Import và cấu hình icon.
  - Dòng 707 - 746: Render `<MapContainer>` để điều hướng lộ trình cho tài xế.
- **BenchmarkLab.jsx** (Test thuật toán): 
  - Dòng 12 - 35: Import và cấu hình icon.
  - Dòng 98 - 160: Render `<MapContainer>` để xem trực quan kết quả thuật toán.

## 2. Sử dụng OR-Tools (Tối ưu hóa bài toán CVRP)
Giải pháp thuật toán VRP sử dụng Google OR-Tools nằm toàn bộ ở Backend thư mục `backend/transport/`:
- **`vrp_solver.py`**: 
  - **Dòng 5, 6**: Import thư viện OR-Tools (`ortools.constraint_solver`).
  - **Dòng 49 - 170**: Hàm chính `solve_vrp`. Định cấu hình CVRP, khai báo dung lượng xe (Capacity Dimension), Search Parameters (`PATH_CHEAPEST_ARC` & `GUIDED_LOCAL_SEARCH`) và chạy hàm Solve rút ra lộ trình tuyến đường tối ưu.

## 3. Import Excel (Nhập đơn hàng hàng loạt)
Quá trình này được chia làm 2 giai đoạn (Frontend đọc file $\rightarrow$ Parser thành Array JSON gửi Backend $\rightarrow$ Backend lưu DB):
- **Frontend đọc/dịch file Excel (`xlsx` thư viện):** Nằm tại `frontend/src/pages/Orders/Orders.jsx`. 
  - Dòng 5: Import thư viện `xlsx`. 
  - Dòng 163 - 207: Hàm xử lý `FileReader.readAsArrayBuffer()` đọc nội dung file Excel, chuyển đổi các Rows thành mảng JSON.
- **Backend tiếp nhận & lưu Database:** Nằm tại `backend/orders/views.py`.
  - Từ dòng 98 đến 179: API function `bulk_create_orders`. Vòng lặp For xử lý JSON array đơn hàng được parse ở trên và `Order.objects.create` để tạo hàng loạt vào CSDL.

## 4. Xử lý Hash Mật khẩu
Dự án tận dụng xử lý hàm băm mật mã chuẩn của hệ sinh thái Django (`pbkdf2_sha256`) thông qua cơ chế `.set_password()` của Object Relational Mapping (ORM):
- **`backend/authentication/models.py`**: Dòng 15 (Khi tạo mới một User, mật khẩu thô được băm tự động bằng hàm này).
- **`backend/authentication/views.py`**: Dòng 425 (Quá trình Reset hoặc Admin đổi mật khẩu tài khoản User).

## 5. Cài đặt bài toán Balo (Bin Packing)
Hệ thống sử dụng giải thuật **First Fit Decreasing (FFD)** để nhồi đơn hàng vào các xe đang rảnh trước khi chạy OR-Tools tạo Route.
- **Thuật toán lõi**: Logic cài đặt nằm ở file `backend/vehicles/bin_packing.py`, từ dòng 9 đến dòng 44. Mã nguồn sắp xếp đơn hàng theo Trọng lượng/Thể tích giảm dần, rồi rà qua danh sách xe tải, xe nào thỏa mãn thì nạp hàng vào (`bins` array).
- **Trình điều khiển API**: Được gọi trong file `backend/vehicles/views.py`, nằm trong khối dòng 119 - 160 (API method `POST /api/vehicles/pack/`).

## 6. Thiết lập kết nối cơ sở dữ liệu (Database PostgreSQL)
Cấu hình nằm trong file Settings project lõi của Django:
- **`backend/vrp_project/settings.py`**: Từ dòng 107 đến 123.
  - Khối mã code này sử dụng thư viện `dj_database_url` để phiên dịch chuỗi biến môi trường `DATABASE_URL` (dạng `postgres://user:pass@host:port/dbname`) thành JSON dictionary mà Django hiểu được.
  - Nếu thiếu file `.env` config, hệ thống sẽ tự động fallback sang cơ sở dữ liệu mặc định là `sqlite3`.
