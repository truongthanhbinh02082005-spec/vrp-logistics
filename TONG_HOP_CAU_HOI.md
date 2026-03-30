# TỔNG HỢP CÂU HỎI BẢO VỆ ĐỒ ÁN VRP LOGISTICS

Dưới đây là bộ câu hỏi và giải đáp ngắn gọn về các thuật toán và logic cốt lõi trong hệ thống VRP Logistics, được đúc kết từ các thắc mắc thường gặp nhất khi bảo vệ đồ án:

---

## 1. "Khoảng cách chim bay" (Haversine) là gì và so sánh nó với cái gì?

### Khái niệm:
- **Đường chim bay:** Là đường thẳng ngắn nhất nối trực tiếp 2 điểm tọa độ GPS (Vĩ độ/Kinh độ) trên bề mặt cong của trái đất bằng công thức **Haversine**. Nó bỏ qua mọi yếu tố đường xá (ngõ hẻm, nhà cửa, đường một chiều).
- **Cách sinh tọa độ:** Hệ thống lấy địa chỉ chữ (Text) từ người dùng (ví dụ: *123 Lê Lợi*) $\rightarrow$ Chạy qua API Geocoding (bản đồ) $\rightarrow$ Trả về Tọa độ GPS $\rightarrow$ Bỏ vào công thức tính ra khoảng cách.

### Trong báo cáo, chúng ta đang so sánh cái gì?
Chúng ta đang so sánh **Hai cách chia lộ trình chở hàng** (Tất cả đều dùng thước đo là Đường chim bay):
- **Cái chưa tối ưu (Baseline):** Cách chia của con người hoặc chia tuần tự ngẫu nhiên. Ví dụ: Rải bừa lịch cho 3 xe mất tổng cộng 160 km đường chim bay.
- **Cái đã tối ưu (OR-Tools):** Máy tính tự động gom điểm thông minh. Cùng 3 xe đó nhưng lược bỏ các chu trình thừa, chỉ mất 100 km đường chim bay.
$\Rightarrow$ Kết luận: Thuật toán hiệu quả, tiết kiệm được 37.5% quãng đường.

### Hướng phát triển (Phần 5):
Khoảng cách chim bay không sát thực tế (vì xe tải không thể đâm xuyên tòa nhà). Tương lai dự án sẽ thay thế bằng **Distance Matrix API của Google Maps** để tính ra số km đường bộ thực tế mà xe tải phải chạy.

---

## 2. Vì sao dùng VRP (OR-Tools) mà không dùng Dijkstra?

- **Thuật toán Dijkstra:** Chỉ giải quyết bài toán "Đi đường nào từ điểm A đến điểm B cho nhanh nhất". Nó không biết phải làm giao hàng cho 50 điểm thì đi nhà nào trước, nhà nào sau.
- **Thuật toán VRP (Vehicle Routing Problem):** Giải quyết bài toán "Tổ hợp". Nó sẽ nhìn tổng thể 50 điểm giao hàng lúc sáng sớm, hoán vị thử hàng nghìn cách và lập dàn ý: *Đưa 20 đơn này cho Xe 1 đi theo thứ tự C-D-E, 30 đơn kia cho Xe 2 đi theo thứ tự F-G... sao cho cuối ngày tổng quãng đường cả 2 xe là thấp nhất*. 
$\Rightarrow$ Tóm lại: Dijkstra là công cụ *dò đường đi*, VRP là bộ não *sắp xếp lịch trình*.

---

## 3. "OR-Tools có trọng lượng (Capacity)" nghĩa là sao? Bài toán CVRP.

- Thuật ngữ chuyên ngành là **CVRP (Capacitated Vehicle Routing Problem).**
- Nghĩa là hệ thống VRP đã được gắn một "Cái cân ảo". Nó nhận vào 2 tham số:
  1. Thùng xe tải này chứa được bao nhiêu ký?
  2. Mỗi cục hàng nặng bao nhiêu ký?
- Gặp VRP bình thường, máy tính có thể bắt 1 xe ghé 50 điểm (làm xe quá tải sập gầm). Nhưng với CVRP (OR-Tools), vừa vẽ đường nó vừa nhẩm cộng số ký. Nếu thùng xe đầy ở điểm thứ 15, nó buộc xe đó đi về kho, và quăng 35 cục hàng còn lại sang cho xe tải thứ 2 lo. 

---

## 4. Nó có giống thuật toán xếp Balo (Bin Packing) không?

Vừa có nét tương đồng, vừa khác biệt mục đích tối thượng:
- **Giống nhau:** Đều bị giới hạn về không gian/cân nặng (không nhét quá tải).
- **Khác nhau về mục đích:**
  - **Bài toán Balo (Bin Packing):** Thuật toán *First Fit Decreasing (FFD)* chỉ cố nhét cho đầy xe, ít lãng phí không gian nhất. Nó **KHÔNG QUAN TÂM** các cục hàng nằm ở đâu trên bản đồ (lỡ chung 1 xe mà 1 đơn ở Thủ Đức, 1 đơn Củ Chi thì tài xế khóc ròng).
  - **OR-Tools (CVRP):** Vừa phải nhét không lố ký, vừa phải **QUAN TÂM ĐƯỜNG ĐI**. Nó thà nhét 3 cục hàng (dù xe mới đầy một nửa), nhưng 3 điểm chung xe đó nằm khít rịt cạnh nhau trên đường, giúp tiết kiệm xăng và thời gian tối đa.
- **Sự kết hợp trong dự án:** Bin Packing dùng làm phễu lọc đầu tiên để gom mẻ hàng lớn cho các xe. Kế đến OR-Tools vào cuộc để vẽ đường ngoằn ngoèo lên bản đồ và gạt các đơn hàng đi trái tuyến sang xe khác.
