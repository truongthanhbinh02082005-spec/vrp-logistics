# Hướng dẫn từng bước Deploy lên Render (VRP Logistics)

Làm theo đúng 3 bước này để đưa web của bạn lên mạng:

## Bước 1: Đẩy code mới nhất lên GitHub
Mở Terminal (PowerShell hoặc CMD) tại thư mục dự án và chạy các lệnh sau:

```bash
git add .
git commit -m "Fix API URL and prepare for Render deployment"
git push
```
*(Nếu bạn chưa kết nối GitHub, hãy đảm bảo repository trên GitHub của bạn đã được cập nhật bản mới nhất này)*.

---

## Bước 2: Tạo dự án trên Render bằng Blueprint
Render có tính năng "Blueprint" giúp đọc file `render.yaml` tôi đã chuẩn bị sẵn để tự động cài đặt mọi thứ (Database + Web App).

1.  Truy cập [Render Dashboard](https://dashboard.render.com/).
2.  Nhấn nút **New +** -> Chọn **Blueprint**.
3.  Kết nối với tài khoản GitHub của bạn.
4.  Chọn repository `vrp-logistics`.
5.  **Service Group Name**: Đặt tên bất kỳ (ví dụ: `vrp-logistics-group`).
6.  Render sẽ hiện ra danh sách các dịch vụ nó sẽ tạo (Postgres và vrp-app).
7.  Nhấn **Apply**.

---

## Bước 3: Theo dõi và Kiểm tra
1.  Render sẽ bắt đầu tạo Database trước, sau đó là Web App.
2.  Nhấn vào dịch vụ **vrp-app** để xem Logs. 
    *   Bạn sẽ thấy nó chạy `npm install`, `npm run build` (cho Frontend) và sau đó là cài đặt Python.
    *   Cuối cùng, nó sẽ chạy `python manage.py migrate` và khởi động Gunicorn.
3.  Khi trạng thái báo **"Live"** (màu xanh), bạn sẽ thấy một đường link ở phía trên (ví dụ: `https://vrp-app-xxxx.onrender.com`).
4.  Nhấp vào link đó để vào trang web của bạn.

### Một số lưu ý quan trọng:
- **Gói Free**: Web của bạn sẽ "đi ngủ" nếu không có ai truy cập trong 15 phút. Lần truy cập tiếp theo sẽ mất khoảng 30s-1 phút để khởi động lại.
- **Database Free**: Sẽ bị xóa sau 30 ngày trên Render (đây là chính sách của họ cho bản miễn phí). Bạn nên lưu ý sao lưu dữ liệu nếu cần dùng lâu dài.
- **Secret Key**: Render sẽ tự tạo một SECRET_KEY bảo mật cho bạn thông qua file `render.yaml`.
