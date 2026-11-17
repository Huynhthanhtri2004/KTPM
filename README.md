# ĐỒ ÁN CUỐI KỲ: HỆ THỐNG KIỂM THỬ TỰ ĐỘNG (SELENIUM + PAGE OBJECT MODEL)

> **Môn học**: Kiểm thử phần mềm / Đảm bảo chất lượng phần mềm  
> **Chủ đề**: Kiểm thử tự động tính năng Xác thực (Đăng nhập & Đăng xuất) trên website Thương mại điện tử  
> **Kiến trúc**: Mô hình hướng đối tượng trang **Page Object Model (POM)** chuẩn công nghiệp  
> **Công nghệ**: Python 3, Selenium WebDriver, openpyxl, PyYAML, python-dotenv  

---

## 1. Cấu trúc thư mục chuẩn Page Object Model

Dự án được phân tách độc lập và chuyên nghiệp theo mô hình chuẩn của Anh Tester:

```
KTPM/
├── src/
│   ├── base/
│   │   ├── base_setup.py          # Quản lý WebDriver (khởi tạo, headless, timeouts, reset session, teardown)
│   │   └── validate_helper.py     # Bộ công cụ UI Actions an toàn (click, set_text, waits, scroll, fallback JS)
│   │
│   ├── pages/
│   │   ├── base_page.py           # Lớp cha của toàn bộ các đối tượng trang (kế thừa ValidateHelper)
│   │   ├── home_page.py           # Xử lý trang chủ (nút Login trên Header)
│   │   └── signin_page.py         # Xử lý trang đăng nhập (locators, submit, alert error, logout)
│   │
│   └── testcases/
│       └── test_signin.py         # 19 test case hoàn chỉnh (LOGIN_001 -> LOGIN_019)
│
├── resources/                     # Thư mục tài nguyên dữ liệu và cấu hình
│   ├── config.yaml                # Cấu hình website URL, trình duyệt, thời gian chờ
│   ├── locators.yaml              # Object Repository lưu trữ định vị phần tử
│   ├── .env                       # Biến môi trường bảo mật tài khoản (ADMIN_EMAIL, ADMIN_PASS)
│   ├── .env.example               # Mẫu khai báo biến môi trường
│   └── testdata/
│       └── login_keywords.xlsx    # Bảng đặc tả và dữ liệu kiểm thử
│
├── test-output/                   # Thư mục kết xuất báo cáo và bằng chứng kiểm thử
│   ├── reports/
│   │   ├── report.html            # Báo cáo kết quả dạng trang web trực quan, chuyên nghiệp (Tiếng Anh)
│   │   └── results.xlsx           # Báo cáo kết quả Excel (kèm Sheet Summary thống kê)
│   └── screenshots/               # Ảnh chụp màn hình bằng chứng tương ứng từng test case
│
├── main.py                        # Điểm khởi chạy chính duy nhất của toàn bộ dự án
├── requirements.txt               # Danh sách thư viện phụ thuộc
└── README.md                      # Tài liệu hướng dẫn đồ án
```

---

## 2. Danh mục 19 Ca kiểm thử chuẩn hóa (LOGIN_001 -> LOGIN_019)

Toàn bộ 19 ca kiểm thử được đánh số thứ tự liên tục, áp dụng các kỹ thuật thiết kế ca kiểm thử chuẩn mực:

### Nhóm 1: Kiểm thử tích cực & tiêu cực (Positive & Negative Testing)
- `LOGIN_001`: Đăng nhập thành công với tài khoản và mật khẩu hợp lệ.
- `LOGIN_002`: Nhập sai mật khẩu.
- `LOGIN_003`: Nhập email chưa đăng ký trên hệ thống.

### Nhóm 2: Kiểm thử xác thực dữ liệu để trống (Field Blank Validations - EP)
- `LOGIN_004`: Để trống trường Email.
- `LOGIN_005`: Để trống trường Mật khẩu.
- `LOGIN_006`: Để trống cả hai trường Email và Mật khẩu.

### Nhóm 3: Kiểm thử phiên làm việc (Session Testing)
- `LOGIN_007`: Đăng xuất khỏi tài khoản sau khi đăng nhập thành công.

### Nhóm 4: Kiểm thử định dạng dữ liệu (Format Validations - EP)
- `LOGIN_008`: Email sai định dạng (thiếu ký tự `@`).
- `LOGIN_009`: Email sai định dạng (thiếu tên miền sau `@`).
- `LOGIN_010`: Email chỉ chứa khoảng trắng.
- `LOGIN_011`: Email đúng cú pháp nhưng tài khoản không tồn tại.
- `LOGIN_012`: Mật khẩu sai nhưng có độ dài hợp lệ.

### Nhóm 5: Phân tích giá trị biên cho độ dài mật khẩu (Boundary Value Analysis - BVA)
- `LOGIN_013`: Mật khẩu 7 ký tự (min - 1, dưới ngưỡng tối thiểu 8).
- `LOGIN_014`: Mật khẩu 8 ký tự (min biên dưới hợp lệ).
- `LOGIN_015`: Mật khẩu 9 ký tự (min + 1).
- `LOGIN_016`: Mật khẩu 19 ký tự (max - 1).
- `LOGIN_017`: Mật khẩu 20 ký tự (max biên trên hợp lệ).
- `LOGIN_018`: Mật khẩu 21 ký tự (max + 1, vượt quá ngưỡng tối đa 20).
- `LOGIN_019`: Mật khẩu rỗng độ dài 0.

---

## 3. Cài đặt môi trường

Mở Terminal và cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

---

## 4. Hướng dẫn chạy kiểm thử

Chuyển vào thư mục dự án `KTPM`:

```bash
cd KTPM
```

### Các cách chạy linh hoạt:

1. **Chạy thử nhanh 1 hoặc 2 test case (Khuyên dùng khi demo)**:
   ```bash
   python main.py --only LOGIN_004,LOGIN_005
   ```

2. **Chạy toàn bộ 19 test case (Mở giao diện trình duyệt)**:
   ```bash
   python main.py
   ```

3. **Chạy ở chế độ ẩn trình duyệt (Headless Mode - Nhanh và gọn)**:
   ```bash
   python main.py --headless
   ```

4. **Chạy trên trình duyệt khác (Firefox hoặc Edge)**:
   ```bash
   python main.py --browser edge
   # hoặc
   python main.py --browser firefox
   ```

---

## 5. Kết quả và Báo cáo kiểm thử

Toàn bộ kết quả sau khi thực thi được lưu tại thư mục **`test-output/`**:
- **Báo cáo HTML trực quan**: `KTPM/test-output/reports/report.html` (giao diện hiện đại, thẻ thống kê Pass/Fail, bảng kết quả và đường dẫn xem ảnh chụp màn hình).
- **Báo cáo Excel kết quả**: `KTPM/test-output/reports/results.xlsx` (cập nhật cột Status tô màu, Actual Result và sheet Summary).
- **Thư mục ảnh bằng chứng**: `KTPM/test-output/screenshots/` (chứa ảnh chụp màn hình tương ứng với từng test case).
