#### 3.2.2.2. Tầng trực quan hóa bản đồ và tương tác báo cáo (Frontend - React)

Phân hệ Frontend sử dụng thư viện ReactJS để xây dựng giao diện người dùng (UI), giúp người quản trị tương tác với hệ thống và trực quan hóa các kết quả do thuật toán Backend xử lý. Quá trình giao tiếp và theo dõi lộ trình được thể hiện qua các giao diện chức năng như sau:

**a. Giao diện Quản lý Vận tải tổng quan (Hình 1)**
Màn hình này cung cấp cái nhìn tổng quát về tình trạng vận tải của hệ thống. Khu vực bên trái hiển thị danh sách các lộ trình chi tiết. Mỗi lộ trình bao gồm các thông tin mã tuyến, tài xế phụ trách và thanh biểu diễn tỷ lệ lấp đầy (so sánh khối lượng hàng hóa với tải trọng tối đa của xe). Khu vực bên phải sử dụng thư viện Leaflet làm bản đồ tương tác để vẽ các tuyến đường đa sắc và định vị các điểm giao hàng trên không gian thực.
<br><center><span style="color: blue;"><i>(Vị trí chèn Hình 1: Giao diện Quản lý vận tải tổng quan)</i></span></center><br>

**b. Thiết lập tham số hệ thống - Chọn Đơn hàng (Hình 2)**
Để bắt đầu tính toán định tuyến, người quản trị mở hộp thoại (Modal) thiết lập tham số. Tại đây có một hộp kiểm thả xuống dạng đa chọn (Multi-select), cho phép người dùng trích xuất và chọn các đơn hàng cần giao từ cơ sở dữ liệu.
<br><center><span style="color: blue;"><i>(Vị trí chèn Hình 2: Hộp thoại Dropdown chọn đơn hàng cần giao)</i></span></center><br>

**c. Thiết lập tham số hệ thống - Phân bổ Tài xế (Hình 3)**
Chuyển sang bước tiếp theo trong hộp thoại, người dùng tiếp tục sử dụng thực đơn thả xuống để chốt danh sách tài xế (và xe tương ứng) sẽ được lên kế hoạch tham gia giao hàng. Thông tin này giúp thuật toán xác định được giới hạn sức chứa nhằm tính toán bài toán đóng gói.
<br><center><span style="color: blue;"><i>(Vị trí chèn Hình 3: Hộp thoại Dropdown phân công tài xế)</i></span></center><br>

**d. Trạng thái phản hồi chờ xử lý - Loading (Hình 4)**
Ngay khi các định danh tham số được gửi đến Backend thông qua API, ứng dụng khóa thao tác tạm thời và hiển thị giao diện báo trạng thái chờ (Loading Spinner) với thông điệp "Đang chạy thuật toán tối ưu VRP...". Quá trình này giúp ngăn chặn việc gửi trùng lặp yêu cầu trong thời gian máy chủ đang xử lý dữ liệu.
<br><center><span style="color: blue;"><i>(Vị trí chèn Hình 4: Trạng thái Loading hệ thống chờ thuật toán)</i></span></center><br>

**e. Giao diện Modal nổi trên nền bản đồ (Hình 5)**
Hộp thoại cấu hình lộ trình được lập trình hiển thị dưới dạng khung nổi (Overlay) nằm trực tiếp bên trên giao diện bản đồ. Cấu trúc thiết kế này giúp người quản trị duy trì được khả năng quan sát định vị không gian địa lý ngay cả trong lúc khai báo các tham số đầu vào.
<br><center><span style="color: blue;"><i>(Vị trí chèn Hình 5: Giao diện hộp thoại thiết lập tham số nổi trên bản đồ)</i></span></center><br>

**f. Thông báo hoàn tất thuật toán tối ưu (Hình 6)**
**g. Báo cáo Hiệu quả Thuật toán (Hình 7)**
Giao diện Báo cáo Tối ưu cung cấp các số liệu thống kê trực tiếp để đánh giá kết quả của hai thuật toán Bin Packing và OR-Tools thông qua các biểu đồ:
- **Đánh giá thuật toán Bin Packing:** Biểu đồ khối lượng liệt kê tổng trọng lượng của 200 đơn hàng là 32.268 kg, được phân bổ vào 36 xe tải có tổng tải trọng là 36.000 kg. Hệ số lấp đầy ghi nhận ở mức 89,6%. Chỉ số này cho thấy không gian trên các xe được thuật toán sắp xếp và sử dụng hiệu quả.
- **Đánh giá thuật toán OR-Tools:** Biểu đồ quãng đường so sánh khoảng cách di chuyển lý thuyết ban đầu là 1.237,72 km với quãng đường thực tế sau tối ưu là 844,72 km. Tỷ lệ giãn cách chứng minh thuật toán đã tiết kiệm được 31,8% tổng quãng đường so với phương án gốc.
<br><center><span style="color: blue;"><i>(Vị trí chèn Hình 7: Giao diện Báo cáo thống kê hiệu quả thuật toán)</i></span></center><br>

**h. Bảng Ma trận Khoảng cách (Hình 8)**
Hệ thống kết xuất trực tiếp toàn bộ dữ liệu cự ly giữa các mút điểm giao hàng dưới dạng cấu trúc bảng (Grid). Để tăng tính hiển thị của dữ liệu số lượng lớn, giao diện áp dụng định dạng bản đồ nhiệt (Heatmap). Màu sắc của từng ô tự động phân định và được gán dựa theo mức trị số lớn nhỏ của khoảng cách. Chức năng này giúp người quản trị dễ dàng quan sát, kiểm tra chéo và phát hiện nhanh các tuyến khoảng cách cự ly dài hoặc bất hợp lý giữa các điểm chạm giao thông.
<br><center><span style="color: blue;"><i>(Vị trí chèn Hình 8: Bảng dữ liệu Ma trận Khoảng cách định dạng Heatmap)</i></span></center><br>
