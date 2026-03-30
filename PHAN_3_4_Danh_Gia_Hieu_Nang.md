## 3.4. Thiết lập Thực nghiệm và Đánh giá Hiệu năng

### 3.4.1. Môi trường thực nghiệm và Bộ dữ liệu kiểm chứng

#### 3.4.1.1. Cấu hình phần cứng và phần mềm triển khai
Quá trình thực nghiệm được tiến hành trên hệ thống máy tính cá nhân của người quản trị nhằm đảm bảo sát với thực tế vận hành:
- **Phần cứng:** Bộ vi xử lý **Intel Core i5-1135G7** (tốc độ tối đa 4.20 GHz), bộ nhớ **RAM 16GB DDR4**.
- **Phần mềm:** Hệ điều hành Windows, môi trường chạy Python 3.10+, các thư viện Google OR-Tools phiên bản 9.6+, Backend Django và Frontend ReactJS.

#### 3.4.1.2. Sử dụng các bộ dữ liệu chuẩn quốc tế (Benchmark Instances)
Hệ thống được kiểm định thông qua hai bộ dữ liệu chuẩn quốc tế từ thư viện TSPLIB (Augerat A-series), vốn là mốc tham chiếu cho các bài toán VRP trên toàn cầu:
- **Bộ dữ liệu A-n32-k5:** Gồm 31 đơn hàng và 1 kho trung tâm (tổng 32 nút), yêu cầu tối ưu hóa với đội xe 5 chiếc.
- **Bộ dữ liệu A-n33-k5:** Gồm 32 đơn hàng và 1 kho trung tâm (tổng 33 nút), yêu cầu tối ưu hóa với đội xe 5 chiếc.
Việc chạy thực nghiệm trên các bộ dữ liệu này giúp xác nhận khả năng giải quyết các ràng buộc tải trọng (Capacity) và quãng đường của bộ giải OR-Tools so với các nghiệm tối ưu đã được công bố.

#### 3.4.1.3. Áp dụng tập dữ liệu thực tế (Stress Test)
Bên cạnh các bộ dữ liệu chuẩn, hệ thống thực hiện bài kiểm tra áp lực (Stress Test) với tập dữ liệu thực tế gồm **200 đơn hàng** và đội xe **36 phương tiện**. Đây là kịch bản mô phỏng quy mô vận hành của một doanh nghiệp phân phối tầm trung, nhằm kiểm chứng tính ổn định và khả năng hội tụ nghiệm tối ưu của giải thuật trong không gian lời giải có độ phức tạp cao.

### 3.4.2. Chỉ số đánh giá và Phương pháp đo lường

Dựa trên kết quả thực thi thực tế từ công cụ `benchmark_vrp.py`, hiệu năng của hệ thống được tổng hợp thông qua bảng thông số sau:

| Đối tượng thử nghiệm | Số nút (Nodes) | Số xe sử dụng | Quãng đường gốc (km) | Quãng đường tối ưu (km) | Tỷ lệ tiết kiệm | Thời gian xử lý |
|:--- |:---:|:---:|:---:|:---:|:---:|:---:|
| **A-n32-k5** | 32 | 5 | 212.62 | 86.89 | **59.13%** | 10.01 giây |
| **A-n33-k5** | 33 | 5 | 185.90 | 73.17 | **60.64%** | 10.00 giây |
| **200 Đơn hàng** | 201 | 13 | 1165.23 | 199.06 | **82.92%** | 10.04 giây |

#### Phân tích Thuật toán chuyên sâu:
- **Độ phức tạp thời gian (Time Complexity):** Bản chất bài toán VRP là NP-hard. Hệ thống khống chế thời gian phản hồi ở mức **O(T × S)** ($T$: 10s giới hạn, $S$: số bước nhảy láng giềng mỗi giây). Điều này giúp hệ thống giữ được tính ổn định bất kể sự bùng nổ tổ hợp của dữ liệu.
- **Độ phức tạp không gian (Space Complexity):** Lưu trữ Ma trận khoảng cách $N \times N$, tương đương **O(N²)**. Với 200 đơn hàng, ma trận đạt ~40,000 phần tử, chiếm dụng tài nguyên RAM không đáng kể trên cấu hình 16GB.
- **Chỉ số Gap (Optimality Gap):** Tỷ lệ cải thiện quãng đường (82.9% cho tập 200 đơn) minh chứng cho khả năng hội tụ nghiệm cực tốt của Guided Local Search (GLS).
- **Mật độ khoảng cách (Distance Density):** Quãng đường trung bình phục vụ đơn hàng giảm từ 5.8 km xuống còn **0.99 km/đơn**, cho thấy độ nén lộ trình đạt hiệu quả tối ưu hóa cao.

<br><center><span style="color: blue;"><i>(Vị trí chèn Hình: Biểu đồ trực quan hóa Hiệu năng và Gap % của thuật toán)</i></span></center><br>
