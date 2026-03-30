# DÀN Ý BÁO CÁO: HỆ THỐNG VRP LOGISTICS - TỐI ƯU HÓA LỘ TRÌNH VẬN CHUYỂN

## PHẦN 1: TỔNG QUAN (OVERVIEW)

**1.1 Đặt vấn đề và tính cấp thiết**
- Nêu các khó khăn trong quản lý chuỗi cung ứng và giao hàng ở các doanh nghiệp (quản lý đơn hàng thủ công, phân bổ xe kém hiệu quả, lộ trình đi chồng chéo gây tốn kém nhiên liệu).
- Sự cần thiết của việc áp dụng thuật toán tối ưu hóa vào bài toán điều phối xe.

**1.2 Mục tiêu của đề tài**
- Xây dựng hệ thống quản lý logistics toàn diện từ khâu nhập đơn (hỗ trợ Excel), quản lý kho bãi, đến điều hành đội xe.
- Số hóa quy trình làm việc giữa các cấp nhân sự (Quản trị viên, Điều phối viên, Tài xế).
- Tự động hóa quá trình đóng gói hàng (Bin Packing) và vạch lộ trình di chuyển (VRP Optimization).

**1.3 Phạm vi và đối tượng nghiên cứu**
- Hệ thống ứng dụng nền tảng Web App (Client-Server).
- Bài toán trọng tâm: Định tuyến phương tiện có giới hạn tải trọng (Capacitated Vehicle Routing Problem).

---

## PHẦN 2: CƠ SỞ LÝ THUYẾT (THEORETICAL BASIS)

**2.1 Bài toán Định tuyến phương tiện (Vehicle Routing Problem - VRP)**
- Giới thiệu khái niệm VRP và biến thể CVRP (Capacitated VRP - có ràng buộc về tải trọng và thể tích của xe).
- Công thức hoặc mô hình toán học cơ bản: Mục tiêu là cực tiểu hóa tổng quãng đường trong khi đảm bảo không xe nào bị quá tải.

**2.2 Bài toán đóng gói (Bin Packing Problem)**
- Bài toán sắp xếp hàng hóa vào thùng xe.
- Thuật toán **First Fit Decreasing (FFD)**: Sắp xếp các đơn hàng theo chiều giảm dần của khối lượng/thể tích và đưa vào chiếc xe trống đầu tiên đủ sức chứa.

**2.3 Công nghệ và Công cụ tối ưu**
- **Google OR-Tools**: Thư viện giải quyết bài toán tối ưu. Trong dự án, bộ giải Constraint Programming (CP-SAT) được sử dụng để giải VRP.
- Các chiến lược tìm kiếm trong OR-Tools: 
  - *First Solution Strategy*: `PATH_CHEAPEST_ARC` (Tìm đường đi có chi phí cung nhỏ nhất).
  - *Metaheuristic*: `GUIDED_LOCAL_SEARCH` (Tối ưu điểm bộ/tránh bị kẹt ở cực trị địa phương).
- **Công thức Haversine (Haversine Formula)**: Tính toán khoảng cách chim bay theo bề mặt cong của trái đất dựa trên kinh độ (Longitude) và vĩ độ (Latitude) giữa các điểm giao hàng.

---

## PHẦN 3: PHƯƠNG PHÁP THỰC HIỆN (IMPLEMENTATION METHOD)

**3.1 Kiến trúc hệ thống**
- Mô hình Monolithic API (Backend Django REST Framework) và Single Page Application (Frontend React 18).
- Cơ sở dữ liệu: Relational Database (PostgreSQL).

**3.2 Phân quyền và Vai trò (User Roles)**
- Trình bày 4 vai trò chính: Admin (Quản trị), Manager (Quản lý), Dispatcher (Điều phối lộ trình), Driver (Tài xế thực thi).

**3.3 Thiết kế các phân hệ (Modules) trọng tâm**
- **Quản lý Kho (Warehouses) & Đơn hàng (Orders):** Quy trình Import dữ liệu hàng loạt từ Excel, tính toán tọa độ đơn hàng và trừ/cộng dồn sức chứa (volume) của kho.
- **Quản lý Xe (Vehicles) & Lên đơn hàng:** Áp dụng Bin Packing để chọn ra các xe đang rảnh (available) tham gia chuyên chở danh sách hàng.
- **Module Tối ưu Vận chuyển (VRP Solver):**
  - Trình bày flow của `solve_vrp` (trong `vrp_solver.py`): Khởi tạo Distance Matrix bằng Haversine -> Set Callback ràng buộc chi phí (quãng đường) và sức chứa (Demand) -> Thiết lập giới hạn thời gian (10s) -> Solve.
  - Cơ chế *Fallback (Simple Distribution)* dự phòng khi OR-Tools không thể tìm ra lời giải (chia đều đơn cho các xe).

**3.4 Quy trình nghiệp vụ (Workflow)**
- Vẽ (hoặc mô tả) biểu đồ luồng: Import đơn hàng -> Điều phối viên gom đơn & cấp xe -> Backend chạy giải thuật tối ưu tạo Route/Stops -> Tài xế nhận lệnh trên màn hình Driver Interface -> Đi giao, upload ảnh minh chứng -> Admin duyệt Transaction (Giao dịch).

---

## PHẦN 4: KẾT QUẢ THỰC NGHIỆM (EXPERIMENTAL RESULTS)

**4.1 Đánh giá tính năng (Functional Testing)**
- Chạy thử nghiệm hệ thống với lượng dữ liệu mẫu (Ví dụ: 5 xe tải, 50-100 đơn hàng).
- **Kết quả phần mềm**: Chụp các ảnh màn hình tính năng tiêu biểu (Giao diện VRP, Dashboard thống kê tĩnh, App tài xế, Báo cáo giao dịch,...).

**4.2 Đánh giá thuật toán (Algorithmic Performance)**
- Đưa ra so sánh (chạy bằng thuật toán tự động vs lộ trình rải thủ công không tối ưu), chỉ ra tổng chiều dài quãng đường (km) có được rút ngắn như thế nào.
- Chỉ ra thống kê hiệu năng trong thuật toán Bin Packing (Tỷ lệ lấp đầy khoảng không/trọng lượng xe so với phân tĩnh cho xe cố định).
- Trình bày thời gian xử lý khi chạy Google OR-Tools trên thực tế (VD: 10s timeout parameter của solver).

---

## PHẦN 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN (CONCLUSION & FUTURE DEVELOPMENT)

**5.1 Kết luận**
- Hệ thống đã đáp ứng được việc tự động hóa, giải quyết bài toán xếp dỡ và lộ trình xe phức tạp với thời gian thực thi ngắn.
- Giao diện trực quan, chia quyền chặt chẽ, hỗ trợ rất tốt quy trình logistics nội bộ của một doanh nghiệp vận tải.
- Việc áp dụng 2 bài toán Bin Packing và VRP giúp đem lại hiệu suất vận tải tối ưu đáng kể.

**5.2 Hướng phát triển tiếp theo**
- Thay thế khoảng cách chim bay (Haversine) bằng Distance Matrix API thực tế như (Google Maps / OSRM) để mô phỏng tình trạng kẹt xe và đường một chiều chính xác.
- Nâng cấp bài toán thành **VRPTW (VRP with Time Windows)** nhằm hỗ trợ giới hạn thời gian giao trong ngày (Giao trước 12h, Giao ca chiều...).
- Triển khai ứng dụng app Tài xế bằng Native Mobile framework (như React Native/Flutter) nhằm tận dụng background location mapping thay vì web-app.

