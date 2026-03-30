# CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ

## 4.1. Hiệu năng bộ giải và Kết quả tối ưu hóa định lượng

### 4.1.1. Kết quả thực nghiệm trên bộ dữ liệu chuẩn (Benchmark Results)

#### 4.1.1.1. Hiệu năng so sánh trên tập dữ liệu A-n32-k5 và A-n33-k5:
Dưới đây là bảng trích xuất kết quả so sánh giữa mô hình tối ưu của hệ thống (OR-Tools) so với phương án thông thường (Baseline) và nghiệm tối ưu công bố (BKS):

| Instance | n | k | BKS | Baseline | OR-Tools | Gap vs Baseline | Gap vs BKS | Fill Factor | Mật độ | Xe dùng |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A-n32-k5** | 31 | 5 | 784 | 1145 | **784** | **+31.53%** | **+0%** | 82% | 0.0395 | 5/5 |
| **A-n33-k5** | 32 | 5 | 661 | 977 | **661** | **+32.34%** | **+0%** | 89.2% | 0.0484 | 5/5 |

**Phân tích từ bảng chỉ số:**
- **Mức độ cải thiện quãng đường:** So với lộ trình cơ sở (Baseline), thuật toán giúp rút ngắn quãng đường lần lượt là **31.53%** và **32.34%**. Điều này cho thấy sự chênh lệch rất lớn về chi phí vận hành nếu không sử dụng công cụ tối ưu.
- **Khả năng tiếp cận nghiệm tối ưu:** Chỉ số **Gap vs BKS đạt 0%** khẳng định bộ giải đã tìm ra được đáp án lý tưởng nhất cho cả hai bộ dữ liệu chuẩn, không phát sinh sai số so với các giá trị học thuật toàn cầu.
- **Chỉ số lấp đầy (Fill Factor):** Mức độ tận dụng thùng xe đạt từ **82% đến 89.2%**. Đây là con số rất cao, chứng minh thuật toán đã nén hàng hóa vào xe cực kỳ chặt chẽ trước khi tính toán đường đi.

#### 4.1.1.1.2. Trực quan hóa Lộ trình Bản đồ (n32 - Hình 2):
Giao diện bản đồ số cung cấp cái nhìn trực diện nhất về sự chênh lệch hiệu quả giữa hai phương án:

- **Bản đồ OR-Tools (Tối ưu):** Các điểm giao hàng được **gom cụm (clustering)** cực kỳ thông minh. Ta có thể thấy 5 tuyến đường với 5 màu sắc (tím, hồng, cam, xanh lam, xanh lá) tách biệt hoàn toàn. Các phương tiện di chuyển theo các vòng lặp (loops) tối ưu, không hề có tình trạng đi ngược đường hay chồng chéo.
- **Bản đồ Baseline (Mặc định):** Hiển thị bằng các đường nét đứt màu xám đan xen như "mạng nhện". Lộ trình này không có tính toán logic về địa lý, dẫn đến việc xe phải di chuyển quãng đường dài tới **1,145 units**.
- **Hệ số lấp đầy (82%):** Thanh biểu đồ màu cam xác nhận thùng xe được tận dụng tối đa, đảm bảo tính kinh tế trong mỗi chuyến đi.

#### 4.1.1.1.3. Ma trận Khoảng cách EUC_2D (n32 - Hình 3):
Đây là "bản đồ số" mà thuật toán sử dụng để ra quyết định. Ma trận này thể hiện mối quan hệ địa lý giữa 32 nút:

- **Mật độ điểm gần:** Các ô màu xanh lá cây đậm (ví dụ: **C3-C4 chỉ có 3 đơn vị**) là những điểm then chốt. Thuật toán luôn ưu tiên "ghép" các điểm này vào cùng một tuyến xe để tiết kiệm cự ly.
- **Tính đối xứng toàn diện:** Ma trận đối xứng tuyệt đối giúp bộ giải GLS (Guided Local Search) tính toán chi phí di chuyển xuôi-ngược đồng nhất, loại bỏ hoàn toàn sai số.

#### 4.1.1.1.4. Kết quả mô phỏng trên tập dữ liệu n33 (Hình 4):
Đối với tập dữ liệu n33 (33 nút), hệ thống duy trì tính ổn định vượt trội trong cả chỉ số định lượng lẫn trực quan:

- **Tỷ lệ tiết kiệm (32.34%):** Quãng đường giảm từ 977 xuống còn **661 units** (trùng khớp 100% với BKS).
- **Hệ số lấp đầy (89.2%):** Thanh biểu đồ màu xanh lá rực rỡ minh chứng cho việc dồn hàng vào xe đạt hiệu quả gần như tối đa. Việc lấp đầy gần 90% tải trọng xe giúp giảm áp lực cho đội xe và tối ưu hóa nguồn vốn lưu động.
- **Cấu trúc lộ trình:** Bản đồ n33 cho thấy các cụm đơn hàng dầy đặc hơn n32, nhưng OR-Tools vẫn phân tách được 5 tuyến đường rành mạch, không sai sót.

#### 4.1.1.1.5. Ma trận Khoảng cách EUC_2D (n33 - Hình 5):
Ma trận của n33 giải mã bí mật đằng sau con số tiết kiệm 32.34%:

- **Các vùng xanh dầy đặc:** Nút **C4-C17 (6 đơn vị)** hay **C12-C19 (8 đơn vị)** nằm sát nhau hơn so với tập n32. Đây là lý do tại sao hệ số lấp đầy của tập này (89.2%) lại cao hơn hẳn n32.
- **Khả năng bao quát:** Ma trận cung cấp cái nhìn toàn cảnh về khoảng cách từ Depot đến mọi "ngõ ngách". Depot đến C3 chỉ mất 15 đơn vị, là điểm khởi đầu lý tưởng cho hành trình tối ưu.

#### 4.1.1.2. Đánh giá sai số và tốc độ hội tụ
Phân tích thực nghiệm cho thấy Google OR-Tools đạt được lời giải tối ưu (Gap 0%) cho các bài toán quy mô 32-33 nút chỉ trong khoảng thời gian rất ngắn (dưới 1 giây). Tuy nhiên, để đảm bảo tính ổn định tối đa cho mọi kịch bản, hệ thống được cấu hình giới hạn thời gian chạy (Time Limit) là 10 giây, giúp thuật toán Guided Local Search có đủ không gian để rà soát kỹ lưỡng các tổ hợp lộ trình tiềm năng.

### 4.1.2. Kết quả thực nghiệm trên dữ liệu thực tế (Real-world Case Study)

#### 4.1.2.1. So sánh quãng đường gốc và quãng đường tối ưu:
Bài kiểm tra trên tập dữ liệu thực tế gồm **200 đơn hàng** cho thấy sự chênh lệch khổng lồ về hiệu quả kinh tế. Trước khi tối ưu, tổng quãng đường mô phỏng theo phương thức vận hành thủ công lên tới **1.237,72 km**. Sau khi áp dụng bộ giải, con số này giảm xuống còn **844,72 km**, tương đương mức cắt giảm **31,8%**. 

Việc tiết kiệm được gần **400 km** di chuyển trên mỗi chu kỳ giao 200 đơn hàng không chỉ giúp giảm trực tiếp chi phí nhiên liệu mà còn hạn chế đáng kể thời gian cầm lái của tài xế và khấu hao phương tiện, chứng minh tính khả thi cực cao khi áp dụng vào doanh nghiệp quy mô tầm trung.

#### 4.1.2.2. Hiệu quả lấp đầy phương tiện (Fill Rate):
Điểm sáng khác trong kết quả thực nghiệm là vai trò then chốt của giai đoạn Bin Packing (đóng gói thùng xe). Nhờ thuật toán First Fit Decreasing (FFD) được tinh chỉnh, hệ số lấp đầy phương tiện trung bình toàn đội đạt mức ấn tượng: **89,6%**.

Việc duy trì hệ số lấp đầy gần 90% giúp doanh nghiệp huy động số lượng xe ở mức tối thiểu mà vẫn đảm bảo vận chuyển hết 100% khối lượng hàng hóa. Đây là kết quả của việc kết hợp nhịp nhàng giữa hai bài toán: tối ưu hóa không gian chứa (Space optimization) và tối ưu hóa định tuyến (Route optimization).

### 4.1.3. Phân tích tính ổn định và Khả năng mở rộng (Scalability)

Hệ thống thể hiện tính ổn định cao khi mở rộng quy mô dữ liệu (Scalability). Khi số lượng đơn hàng tăng từ 32 nút lên **200 nút** (gấp hơn 6 lần), thời gian tính toán của bộ giải vẫn được duy trì ổn định xung quanh ngưỡng **10 giây** theo đúng cấu hình `time_limit` của OR-Tools.

Dù không gian lời giải bùng nổ tổ hợp theo cấp số nhân, thuật toán Guided Local Search (GLS) vẫn hội tụ được về vùng nghiệm tốt (Local Optima chất lượng cao) trong thời gian cho phép. Điều này khẳng định hệ thống hoàn toàn đủ khả năng đáp ứng nhu cầu thực tế của các trung tâm Logistics lớn với lượng đơn hàng biến động liên tục mà không gặp phải tình trạng treo máy hay quá tải bộ nhớ.

## 4.2. Triển khai hệ thống và Giá trị ứng dụng thực tiễn

### 4.2.1. Triển khai giao diện Dashboard và Trực quan hóa

#### 4.2.1.1. Hiển thị lộ trình trực quan trên bản đồ số
Mô tả cách thức hệ thống biểu diễn các "Route" khác nhau bằng màu sắc và các điểm dừng thông minh.

#### 4.2.1.2. Hệ thống báo cáo chỉ số tối ưu (Optimization Analytics)
Trình bày các biểu đồ phân tích tải trọng, quãng đường và trạng thái đơn hàng thời gian thực.

### 4.2.2. Hiệu quả kinh tế và Đánh giá tác động vận hành

#### 4.2.2.1. Tác động đến chi phí nhiên liệu và khấu hao
Ước tính giá trị tiết kiệm được từ việc cắt giảm quãng đường di chuyển.

#### 4.2.2.2. Tối ưu hóa nguồn lực nhân sự và kho bãi
Phân tích khả năng hỗ trợ ra quyết định của hệ thống trong việc giảm áp lực điều phối thủ công.
