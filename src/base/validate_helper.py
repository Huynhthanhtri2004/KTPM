"""ValidateHelper: Cung cấp các hàm tiện ích tương tác giao diện an toàn (Wrapper UI Actions).
Tương ứng ValidateHelper.java trong cấu trúc Page Object Model của Anh Tester.
"""
import time
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

_BY_MAP = {
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
    "id": By.ID,
    "name": By.NAME,
    "class": By.CLASS_NAME,
    "tag": By.TAG_NAME,
    "link_text": By.LINK_TEXT,
}


def parse_locator(locator):
    """Phân giải chuỗi locator thành tuple (By, selector) nếu chưa phải là tuple."""
    if isinstance(locator, tuple):
        return locator
    if not isinstance(locator, str):
        return By.CSS_SELECTOR, str(locator)
    for prefix, by in _BY_MAP.items():
        if locator.startswith(prefix + "="):
            return by, locator[len(prefix) + 1 :]
    return By.CSS_SELECTOR, locator


class ValidateHelper:
    def __init__(self, driver, default_timeout: float = 25.0):
        self.driver = driver
        self.default_timeout = default_timeout

    def wait_for_page_loaded(self, timeout: float = None):
        """Chờ trình duyệt tải hoàn tất trang (document.readyState == 'complete')."""
        t = timeout or self.default_timeout
        try:
            WebDriverWait(self.driver, t).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass

    def open_url(self, url: str):
        """Mở đường dẫn và chờ trang sẵn sàng."""
        self.driver.get(url)
        self.wait_for_page_loaded()

    def get_current_url(self) -> str:
        """Lấy URL hiện tại của trình duyệt."""
        return self.driver.current_url

    def find_visible_element(self, locator, timeout: float = None):
        """Tìm và trả về phần tử đang hiển thị trên trang."""
        by, val = parse_locator(locator)
        t = timeout or self.default_timeout

        def _find(d):
            try:
                for el in d.find_elements(by, val):
                    try:
                        if el.is_displayed():
                            return el
                    except (StaleElementReferenceException, WebDriverException):
                        continue
            except (StaleElementReferenceException, WebDriverException):
                pass
            return False

        try:
            return WebDriverWait(self.driver, t, poll_frequency=0.5).until(_find)
        except TimeoutException:
            raise TimeoutException(f"Visible element not found for '{locator}' after {t}s")

    def click_element(self, locator, timeout: float = None):
        """Bấm vào phần tử với cơ chế tự động cuộn, retry và fallback JS click."""
        by, val = parse_locator(locator)
        t = timeout or self.default_timeout
        start = time.time()
        last_err = None

        while time.time() - start < t:
            try:
                el = self.find_visible_element(locator, timeout=max(1.0, t - (time.time() - start)))
                try:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', inline: 'center'});", el
                    )
                except WebDriverException:
                    pass
                el.click()
                return
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                last_err = e
                time.sleep(0.5)
            except TimeoutException:
                raise
            except WebDriverException as e:
                last_err = e
                time.sleep(0.5)

        # Fallback bằng Javascript click nếu bị intercept/overlay
        try:
            el = self.driver.find_element(by, val)
            self.driver.execute_script("arguments[0].click();", el)
            return
        except Exception:
            raise TimeoutException(f"Clickable element not found for '{locator}' after {t}s (error: {last_err})")

    def set_text(self, locator, text: str, timeout: float = None):
        """Nhập văn bản vào ô input (hỗ trợ xóa sạch input trên React bằng Backspace)."""
        el = self.find_visible_element(locator, timeout)
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});", el
            )
        except WebDriverException:
            pass
        el.clear()
        current = el.get_attribute("value") or ""
        if current:
            el.send_keys(Keys.END)
            el.send_keys(Keys.BACKSPACE * len(current))
        if text:
            el.send_keys(text)

    def get_text(self, locator, timeout: float = None) -> str:
        """Lấy nội dung văn bản của phần tử."""
        try:
            el = self.find_visible_element(locator, timeout)
            return el.text.strip()
        except TimeoutException:
            return ""

    def is_element_displayed(self, locator, timeout: float = 3.0) -> bool:
        """Kiểm tra phần tử có hiển thị không."""
        try:
            self.find_visible_element(locator, timeout)
            return True
        except TimeoutException:
            return False

    def wait_for_url_contains(self, text: str, timeout: float = None) -> bool:
        """Chờ URL chứa đoạn văn bản mong đợi."""
        t = timeout or self.default_timeout
        try:
            WebDriverWait(self.driver, t, poll_frequency=0.5).until(lambda d: text in d.current_url)
            return True
        except TimeoutException:
            return False

    def wait_for_url_not_contains(self, text: str, timeout: float = None) -> bool:
        """Chờ URL không còn chứa đoạn văn bản."""
        t = timeout or self.default_timeout
        try:
            WebDriverWait(self.driver, t, poll_frequency=0.5).until(lambda d: text not in d.current_url)
            return True
        except TimeoutException:
            return False

    def take_screenshot(self, save_path: str):
        """Chụp ảnh màn hình lưu vào đường dẫn chỉ định."""
        self.driver.save_screenshot(save_path)

