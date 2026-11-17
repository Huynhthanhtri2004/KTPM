"""SignInPage: Quản lý các phần tử và hành vi trên Trang đăng nhập (/signin).
"""
from selenium.webdriver.common.by import By
from src.pages.base_page import BasePage


class SignInPage(BasePage):
    # --- Locators ---
    EMAIL_INPUT = (By.CSS_SELECTOR, 'input[name="email"]')
    PASSWORD_INPUT = (By.CSS_SELECTOR, 'input[name="password"]')
    SUBMIT_BUTTON = (By.CSS_SELECTOR, 'button[type="submit"]')
    ERROR_ALERT = (
        By.CSS_SELECTOR,
        '.chakra-alert, [role="alert"], [role="status"], .chakra-form__error-message',
    )
    LOGOUT_BUTTON = (
        By.XPATH,
        '//*[self::button or self::a or self::p or self::span][contains(translate(normalize-space(.), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "logout") or contains(normalize-space(.), "Đăng xuất")]',
    )

    def __init__(self, driver):
        super().__init__(driver)

    # --- Actions ---
    def enter_email(self, email: str):
        """Nhập email vào trường email."""
        self.helper.set_text(self.EMAIL_INPUT, email)
        return self

    def enter_password(self, password: str):
        """Nhập mật khẩu vào trường password."""
        self.helper.set_text(self.PASSWORD_INPUT, password)
        return self

    def click_submit(self):
        """Bấm nút đăng nhập."""
        self.helper.click_element(self.SUBMIT_BUTTON)
        return self

    def login(self, email: str, password: str):
        """Hàm gộp: Nhập email, mật khẩu và bấm nút Đăng nhập."""
        self.enter_email(email)
        self.enter_password(password)
        self.click_submit()
        return self

    def click_logout(self):
        """Bấm nút đăng xuất."""
        self.helper.click_element(self.LOGOUT_BUTTON)
        return self

    # --- Verifications ---
    def is_login_page_displayed(self, timeout: float = 10.0) -> bool:
        """Kiểm tra xem trang đăng nhập (ô input email) có đang hiển thị không."""
        return self.helper.is_element_displayed(self.EMAIL_INPUT, timeout)

    def is_error_displayed(self, timeout: float = 8.0) -> bool:
        """Kiểm tra có thông báo lỗi hiển thị không."""
        return self.helper.is_element_displayed(self.ERROR_ALERT, timeout)

    def get_error_message(self, timeout: float = 8.0) -> str:
        """Lấy văn bản thông báo lỗi."""
        return self.helper.get_text(self.ERROR_ALERT, timeout)

    def is_login_successful(self, timeout: float = 15.0) -> bool:
        """Kiểm tra đăng nhập thành công (URL không còn chứa /signin)."""
        return self.helper.wait_for_url_not_contains("/signin", timeout)

