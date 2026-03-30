## 3.3. Thiết lập và Giải quyết mô hình tối ưu hóa

### 3.3.1. Mô hình hóa toán học (Đối tượng, Ràng buộc và Hàm mục tiêu)

#### 3.3.1.1. Định nghĩa hàm mục tiêu
Hệ thống sử dụng hàm phản hồi để tính toán chi phí di chuyển giữa các điểm, làm cơ sở cho hàm mục tiêu tối thiểu hóa tổng quãng đường.
- **Vị trí code:** `backend/transport/vrp_solver.py` (Dòng 91-95)
- **Đoạn code xử lý:**
```python
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]
```
- **Giải thích:** Hàm này nhận vào hai tham số `from_index` và `to_index` đại diện cho chỉ mục của điểm đi và điểm đến trong hàng đợi của OR-Tools. Hàm thực hiện chuyển đổi chỉ mục nội bộ thành nút thực tế (`IndexToNode`) và truy xuất giá trị cự ly từ ma trận khoảng cách (`distance_matrix`). Trong thực tế, giá trị trả về đóng vai trò là "chi phí" (Cost) mà thuật toán phải tối thiểu hóa để tìm ra tuyến đường ngắn nhất.

#### 3.3.1.2. Thiết lập các hệ ràng buộc thực tế
Hệ thống áp dụng các ràng buộc về tải trọng xe và không gian xếp hàng để đảm bảo tính khả thi của lộ trình.
- **Vị trí code:** `backend/transport/vrp_solver.py` (Dòng 106-112)
- **Đoạn code xử lý:**
```python
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,  # null capacity slack
    [int(c) for c in vehicle_capacities],  # Vehicle capacities
    True,  # start cumul to zero
    'Capacity'
)
```
- **Giải thích:** Hàm `AddDimensionWithVehicleCapacity` thiết lập thuộc tính "Sức chứa" cho mô hình. Tham số `demand_callback_index` liên kết với lượng hàng mỗi đơn, tham số thứ ba là mảng `vehicle_capacities` chứa tải trọng thực tế của từng xe tham gia giao hàng. Đoạn code này giải quyết vấn đề quá tải bằng cách ngăn thuật toán gán thêm đơn hàng khi tổng tích lũy (Cumul) chạm ngưỡng sức tải của xe.

### 3.3.2. Triển khai thuật toán và Cấu hình bộ giải (Solver)

#### 3.3.2.1. Cấu hình thư viện Google OR-Tools
Khai báo trình quản lý chỉ mục và giới hạn thời gian thực thi để kiểm soát luồng xử lý.
- **Vị trí code:** `backend/transport/vrp_solver.py` (Dòng 81-85 và 122)
- **Đoạn code xử lý:**
```python
manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, 0)
search_parameters.time_limit.seconds = 10
```
- **Giải thích:** Đối tượng `RoutingIndexManager` khởi tạo ma trận lưới với `num_locations` (tổng điểm giao) và `num_vehicles` (số xe), với tham số `0` xác định kho bãi (Depot) là điểm bắt đầu. Tham số `time_limit.seconds = 10` giới hạn thời gian giải thuật trong 10 giây, giải quyết bài toán hiệu năng, đảm bảo người dùng không phải chờ đợi quá lâu khi xử lý tập dữ liệu lớn.

#### 3.3.2.2. Chiến lược tìm kiếm Metaheuristic - Guided Local Search (GLS)
Sử dụng GLS để cải thiện chất lượng nghiệm và vượt qua các điểm tối ưu cục bộ.
- **Vị trí code:** `backend/transport/vrp_solver.py` (Dòng 119-121)
- **Đoạn code xử lý:**
```python
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
)
```
- **Giải thích:** Đoạn code thiết lập chiến lược tìm kiếm thứ cấp (Metaheuristic). GLS hoạt động bằng cách thay đổi hàm mục tiêu thông qua việc gán các hình phạt (Penalty) vào các cung đường đã đi qua nhiều lần. Trong thực tế, tham số này giúp thuật toán "thoát" khỏi những phương án trung bình để tìm được những lộ trình đột phá, giúp tiết kiệm quãng đường hơn so với các phương pháp tìm kiếm thông thường.

#### 3.3.2.3. Giải thuật Tham lam (Greedy Algorithm) trong bài toán đóng gói
Sắp xếp và phân bổ hàng hóa dựa trên thuật toán First Fit Decreasing (FFD) trước khi định tuyến.
- **Vị trí code:** `backend/vehicles/bin_packing.py` (Dòng 45-68)
- **Đoạn code xử lý:**
```python
for order in sorted_orders:
    for bin in bins:
        if order_weight <= remaining_weight and order_volume <= remaining_volume:
            bin['orders'].append(order)
            bin['current_weight'] += order_weight
            break
```
- **Giải thích:** Vòng lặp này duyệt qua danh sách `sorted_orders` (đơn hàng đã xếp giảm dần theo trọng lượng). Với mỗi đơn hàng, thuật toán tìm `bin` (xe tải) đầu tiên còn đủ `remaining_weight` (trọng tải trống) và `remaining_volume` (thể tích trống). Đây là giải thuật tham lam giúp tối ưu hóa hệ số lấp đầy của phương tiện ngay từ bước chuẩn bị dữ liệu, đảm bảo xe được chất hàng kín nhất có thể trước khi tính toán đường đi.
