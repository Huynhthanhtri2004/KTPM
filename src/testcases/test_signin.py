"""SignInTest: Chứa các ca kiểm thử cho chức năng Đăng nhập / Đăng xuất theo mô hình Page Object Model.
Đã chuẩn hóa thứ tự liên tục từ LOGIN_001 đến LOGIN_019.
"""
import os
import unittest
from src.base.base_setup import BaseSetup
from src.pages.home_page import HomePage
from src.pages.signin_page import SignInPage


class SignInTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Khởi tạo BaseSetup và nạp tài khoản admin từ môi trường."""
        cls.base_setup = BaseSetup()
        cls.admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        cls.admin_pass = os.environ.get("ADMIN_PASS", "Admin@12345")

    def setUp(self):
        """Mỗi test case bắt đầu với phiên trình duyệt mới và điều hướng vào trang chủ."""
        if not hasattr(self, "driver") or self.driver is None:
            self.driver = self.base_setup.init_driver()
        self.base_setup.reset_session()
        self.home_page = HomePage(self.driver, self.base_setup.base_url)
        self.home_page.open_home_page()
        self.signin_page = self.home_page.click_header_login()

    def tearDown(self):
        """Dọn dẹp sau mỗi ca kiểm thử."""
        pass

    @classmethod
    def tearDownClass(cls):
        """Đóng toàn bộ trình duyệt sau khi chạy xong bộ test."""
        cls.base_setup.quit_driver()

    # =========================================================================
    # POSITIVE & NEGATIVE TEST CASES (LOGIN_001 -> LOGIN_003)
    # =========================================================================

    def test_LOGIN_001_valid_credentials(self):
        """LOGIN_001: Đăng nhập thành công với tài khoản và mật khẩu hợp lệ."""
        self.signin_page.login(self.admin_email, self.admin_pass)
        self.assertTrue(
            self.signin_page.is_login_successful(timeout=15),
            "Expected URL not to contain '/signin' after successful login."
        )

    def test_LOGIN_002_incorrect_password(self):
        """LOGIN_002: Đăng nhập thất bại khi nhập sai mật khẩu."""
        self.signin_page.login(self.admin_email, "WrongPassword@123")
        self.assertIn("/signin", self.driver.current_url)
        self.assertTrue(
            self.signin_page.is_error_displayed(),
            "Expected error alert to be displayed when entering an incorrect password."
        )

    def test_LOGIN_003_unregistered_email(self):
        """LOGIN_003: Đăng nhập thất bại với email chưa đăng ký."""
        self.signin_page.login("unregistered_user_99999@test.com", "Password@123")
        self.assertIn("/signin", self.driver.current_url)
        self.assertTrue(
            self.signin_page.is_error_displayed(),
            "Expected error alert to be displayed for unregistered email."
        )

    # =========================================================================
    # VALIDATION TEST CASES: FIELD BLANKS (LOGIN_004 -> LOGIN_006)
    # =========================================================================

    def test_LOGIN_004_leave_email_blank(self):
        """LOGIN_004: Để trống ô Email."""
        self.signin_page.login("", "AnyPassword@123")
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_005_leave_password_blank(self):
        """LOGIN_005: Để trống ô Mật khẩu."""
        self.signin_page.login(self.admin_email, "")
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_006_leave_both_fields_blank(self):
        """LOGIN_006: Để trống cả hai trường Email và Mật khẩu."""
        self.signin_page.login("", "")
        self.assertIn("/signin", self.driver.current_url)

    # =========================================================================
    # SESSION TESTING: LOGOUT (LOGIN_007)
    # =========================================================================

    def test_LOGIN_007_logout(self):
        """LOGIN_007: Đăng xuất khỏi hệ thống sau khi đăng nhập thành công."""
        self.signin_page.login(self.admin_email, self.admin_pass)
        self.assertTrue(
            self.signin_page.is_login_successful(timeout=15),
            "Must be logged in before testing logout."
        )
        self.signin_page.click_logout()
        self.home_page.open_home_page()
        self.assertTrue(
            self.home_page.helper.is_element_displayed(self.home_page.HEADER_LOGIN_BUTTON, timeout=8),
            "Expected Header Login button to be visible after logging out."
        )

    # =========================================================================
    # VALIDATION TEST CASES: FORMATS & DATA (LOGIN_008 -> LOGIN_012)
    # =========================================================================

    def test_LOGIN_008_email_without_at_symbol(self):
        """LOGIN_008: Email sai định dạng - thiếu ký tự @."""
        self.signin_page.login("invalidemailformat.com", "Password@123")
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_009_email_missing_domain(self):
        """LOGIN_009: Email sai định dạng - thiếu tên miền sau @."""
        self.signin_page.login("user@", "Password@123")
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_010_email_contains_whitespace_only(self):
        """LOGIN_010: Email chỉ chứa khoảng trắng."""
        self.signin_page.login("   ", "Password@123")
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_011_valid_email_format_unregistered(self):
        """LOGIN_011: Email đúng định dạng nhưng không tồn tại trên hệ thống."""
        self.signin_page.login("notexists_888@somedomain.org", "Pass@12345")
        self.assertIn("/signin", self.driver.current_url)
        self.assertTrue(self.signin_page.is_error_displayed())

    def test_LOGIN_012_incorrect_password_valid_length(self):
        """LOGIN_012: Mật khẩu sai nhưng có độ dài hợp lệ (10 ký tự)."""
        self.signin_page.login(self.admin_email, "WrongLength10")
        self.assertIn("/signin", self.driver.current_url)
        self.assertTrue(self.signin_page.is_error_displayed())

    # =========================================================================
    # BOUNDARY VALUE ANALYSIS (BVA - PASSWORD LENGTH) (LOGIN_013 -> LOGIN_019)
    # =========================================================================

    def test_LOGIN_013_password_length_7_min_minus_1(self):
        """LOGIN_013: Độ dài mật khẩu 7 ký tự (min - 1, dưới ngưỡng tối thiểu 8)."""
        self.signin_page.login(self.admin_email, "a" * 7)
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_014_password_length_8_min(self):
        """LOGIN_014: Độ dài mật khẩu 8 ký tự (min biên dưới hợp lệ)."""
        self.signin_page.login(self.admin_email, "a" * 8)
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_015_password_length_9_min_plus_1(self):
        """LOGIN_015: Độ dài mật khẩu 9 ký tự (min + 1)."""
        self.signin_page.login(self.admin_email, "a" * 9)
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_016_password_length_19_max_minus_1(self):
        """LOGIN_016: Độ dài mật khẩu 19 ký tự (max - 1)."""
        self.signin_page.login(self.admin_email, "a" * 19)
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_017_password_length_20_max(self):
        """LOGIN_017: Độ dài mật khẩu 20 ký tự (max biên trên hợp lệ)."""
        self.signin_page.login(self.admin_email, "a" * 20)
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_018_password_length_21_max_plus_1(self):
        """LOGIN_018: Độ dài mật khẩu 21 ký tự (max + 1, vượt quá giới hạn 20)."""
        self.signin_page.login(self.admin_email, "a" * 21)
        self.assertIn("/signin", self.driver.current_url)

    def test_LOGIN_019_password_length_0_empty(self):
        """LOGIN_019: Độ dài mật khẩu 0 ký tự (rỗng)."""
        self.signin_page.login(self.admin_email, "")
        self.assertIn("/signin", self.driver.current_url)
