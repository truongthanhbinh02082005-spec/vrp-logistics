# HƯỚNG DẪN CHI TIẾT TỪNG BƯỚC ĐỂ LẤY LINK WEB (RENDER)

Chào bạn, đây là bản hướng dẫn "cầm tay chỉ việc" nhất để giúp bạn đưa dự án lên mạng. Hãy làm theo đúng thứ tự này nhé:

---

## GIAI ĐOẠN 1: ĐƯA CODE LÊN GITHUB (Nơi lưu trữ mã nguồn)

Nếu bạn đã có code trên GitHub rồi, hãy bỏ qua bước này. Nếu chưa, hãy làm như sau:

1. **Tạo tài khoản GitHub**: Nếu chưa có, hãy đăng ký tại [github.com](https://github.com/).
2. **Tạo Repository mới**:
   - Nhấn vào dấu **+** ở góc trên bên phải trang web, chọn **New repository**.
   - Đặt tên là `vrp-logistics`.
   - Chọn **Public**.
   - Nhấn nút **Create repository**.
3. **Mở terminal tại máy bạn**:
   - Mở thư mục `f:\vrp_duphong`.
   - Chuột phải vào khoảng trắng, chọn "Open in Terminal" hoặc "Open PowerShell here".
4. **Chạy các lệnh sau (Copy từng dòng một):**
   ```bash
   git init
   git add .
   git commit -m "Thiết lập Docker và Render"
   git branch -M main
   git remote add origin https://github.com/TÊN_TÀI_KHOẢN_CỦA_BẠN/vrp-logistics.git
   git push -u origin main
   ```
   *(Thay `TÊN_TÀI_KHOẢN_CỦA_BẠN` bằng tên thật của bạn trên GitHub)*

---

## GIAI ĐOẠN 2: TRIỂN KHAI LÊN RENDER (Nơi chạy web)

1. **Đăng nhập Render**: Truy cập [dashboard.render.com](https://dashboard.render.com/) và chọn "Sign in with GitHub".
2. **Bắt đầu triển khai (Dùng Blueprint)**:
   - Tại màn hình chính, nhấn nút **New +** (màu xanh).
   - Chọn dòng **Blueprint**. (Đây là cách để Render đọc file `render.yaml` mà tôi đã tạo).
3. **Kết nối Repository**:
   - Bạn sẽ thấy danh sách các dự án GitHub của mình. Hãy nhấn nút **Connect** bên cạnh dự án `vrp-logistics`.
4. **Cấu hình Blueprint**:
   - Ở mục **Service Group Name**, bạn đặt tên tùy ý (ví dụ: `vrp-system`).
   - Nhấn nút **Approve**.
5. **Đợi hệ thống "xây dựng" (Build)**:
   - Bạn sẽ thấy Render bắt đầu tạo 3 thứ: `vrp-db`, `vrp-backend`, và `vrp-frontend`.
   - Quá trình này mất khoảng **10 đến 15 phút** vì Render phải cài đặt các thư viện Python cho backend và build thư mục React cho frontend.

---

## GIAI ĐOẠN 3: LẤY LINK WEB VÀ SỬ DỤNG

1. **Tìm link**: Khi cột "Status" của `vrp-frontend` hiện chữ **Live** màu xanh, hãy nhấn vào đó.
2. **Mở Web**: Bạn sẽ thấy một đường link dạng `https://vrp-frontend-xxxx.onrender.com`. Đó chính là link web của bạn!
3. **Lưu ý quan trọng**:
   - **Lỗi 502/Trang trắng**: Đừng lo, đó là lúc Backend đang khởi động. Hãy đợi thêm 1-2 phút rồi F5 lại trang.
   - **Gói Miễn phí**: Sau khi bạn tắt web đi 15 phút, nó sẽ tự "ngủ". Khi mở lại sẽ hơi chậm vì nó cần thời gian khởi động lại.

---

## CÁC LỖI THƯỜNG GẶP VÀ CÁCH XỬ LÝ

- **Lệnh `git` không nhận diện**: Bạn cần cài đặt Git tại [git-scm.com](https://git-scm.com/).
- **Build bị Fail**: Hãy nhấn vào dòng báo "Fail" trên Render để xem log. Đa số là do thiếu thư viện trong `requirements.txt` (Tôi đã kiểm tra kỹ rồi nên tỉ lệ này rất thấp).

Bạn hãy bắt đầu từ **GIAI ĐOẠN 1** nhé. Nếu vướng ở lệnh nào, hãy nhắn tôi ngay!
