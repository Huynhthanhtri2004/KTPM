"""HomePage: Quản lý các phần tử và hành vi trên Trang chủ.
"""
from selenium.webdriver.common.by import By
from src.pages.base_page import BasePage


class HomePage(BasePage):
    # --- Locators ---
    HEADER_LOGIN_BUTTON = (By.CSS_SELECTOR, 'a[href="/signin"] button, a[href="/signin"]')

    def __init__(self, driver, base_url: str = "https://e-commerce-for-testing.onrender.com"):
        super().__init__(driver)
        self.base_url = base_url.rstrip("/")

    # --- Actions ---
    def open_home_page(self):
        """Mở trang chủ và chờ DOM hoàn tất."""
        self.helper.open_url(self.base_url + "/")
        return self

    def click_header_login(self):
        """Bấm vào nút Login trên thanh Header để chuyển đến trang đăng nhập."""
        self.helper.click_element(self.HEADER_LOGIN_BUTTON)
        # Chờ chuyển hướng sang trang /signin
        self.helper.wait_for_url_contains("/signin", timeout=15)
        from src.pages.signin_page import SignInPage
        return SignInPage(self.driver)

