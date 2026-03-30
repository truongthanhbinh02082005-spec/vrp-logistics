# Hướng dẫn triển khai lên Zeabur (MIỄN PHÍ - KHÔNG CẦN THẺ)

Nếu Koyeb bắt nhập thẻ tín dụng, bạn hãy chuyển sang dùng **Zeabur**. Đây là nền tảng hỗ trợ Docker rất mạnh mẽ, miễn phí và đặc biệt là **không yêu cầu thẻ tín dụng** để bắt đầu.

## Phần 1: Chuẩn bị Database (Postgres) trên Zeabur

1.  Truy cập [Zeabur.com](https://zeabur.com/) và đăng nhập bằng GitHub.
2.  Nhấn **Create Project**.
3.  Nhấn **Create Service** -> chọn **Marketplace**.
4.  Tìm và chọn **PostgreSQL**.
5.  Zeabur sẽ tự động tạo một Database Postgres cho bạn.
6.  Vào tab **Instruction** của dịch vụ Postgres vừa tạo, bạn sẽ thấy các thông tin như `Host`, `Port`, `Password`, v.v.
    *   Zeabur cung cấp biến môi trường tự động, nhưng bạn cũng có thể lấy chuỗi `Connection String` tại đây.

---

## Phần 2: Triển khai Ứng dụng (Web Service)

1.  Trong cùng Project đó, nhấn lại nút **Create Service**.
2.  Chọn **GitHub** và chọn repository của bạn (`vrp-logistics`).
3.  Zeabur sẽ tự động nhận diện `Dockerfile` ở thư mục gốc.
4.  Vào tab **Variables** (Biến môi trường) và thêm:
    | Key | Value | Ghi chú |
    | :--- | :--- | :--- |
    | `DATABASE_URL` | (Chuỗi kết nối lấy từ dịch vụ Postgres trên) | Quan trọng nhất |
    | `PORT` | `10000` | Port ứng dụng |
    | `DEBUG` | `False` | |
    | `ALLOWED_HOSTS` | `*` | |
    | `SECRET_KEY` | `tôi_yêu_logistics_2025` | |

5.  Vào tab **Settings**:
    *   Trong mục **Networking**, nhấn **Generate Domain**. Bạn sẽ nhận được một link có dạng `xxx.zeabur.app`.
6.  Zeabur sẽ bắt đầu Build và Deploy tự động.

---

## Một lựa chọn khác: Railway.app

**Railway** cũng rất tốt và cho dùng thử 30 ngày (có $5 credit) không cần thẻ.
1.  Vào [Railway.app](https://railway.app/).
2.  Chọn **Provision PostgreSQL** trước.
3.  Sau đó chọn **Deploy from GitHub repo**.
4.  Cấu hình biến môi trường tương tự như trên.

---

## Tại sao các nền tảng bắt nhập thẻ?
Đa số các bên như Koyeb, Render, Fly.io bắt nhập thẻ là để **xác minh danh tính** (Identity Verification) nhằm tránh việc mọi người tạo hàng ngàn tài khoản ảo để đào tiền ảo (mining) hoặc spam. Họ không trừ tiền của bạn ở gói Free, nhưng nó gây khó khăn nếu bạn chưa có thẻ.

**Lời khuyên**: Hãy thử **Zeabur** trước vì nó hiện tại là bên "thoáng" nhất cho sinh viên và demo project.
