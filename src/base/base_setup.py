"""BaseSetup: Khởi tạo và quản lý cấu hình trình duyệt WebDriver.
Tương ứng BaseSetup.java trong cấu trúc Page Object Model của Anh Tester.
"""
import os
import urllib.request
import yaml
from dotenv import load_dotenv
from selenium import webdriver

# Nạp file biến môi trường .env từ resources/ hoặc thư mục hiện tại
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ENV_PATH = os.path.join(_BASE_DIR, "resources", ".env")
if os.path.exists(_ENV_PATH):
    load_dotenv(_ENV_PATH)
else:
    load_dotenv()


def load_config() -> dict:
    """Đọc file cấu hình config.yaml từ thư mục resources/."""
    cfg_path = os.path.join(_BASE_DIR, "resources", "config.yaml")
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(_BASE_DIR, "config.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {
        "base_url": "https://e-commerce-for-testing.onrender.com",
        "browser": "chrome",
        "headless": False,
        "timeouts": {"page_load": 90, "element": 25},
    }


def wake_server(url: str, timeout: int = 90):
    """Đánh thức server Render nếu đang ở trạng thái ngủ đông (Sleep)."""
    print(f"Waking up server {url} (may take up to {timeout}s)...")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        urllib.request.urlopen(req, timeout=timeout).read(1)
        print("Server is ready.")
    except Exception as e:
        print(f"[WARNING] Server did not respond ({e}), proceeding anyway.")


class BaseSetup:
    def __init__(self, browser: str = None, headless: bool = None):
        self.config = load_config()
        self.base_url = self.config.get("base_url", "https://e-commerce-for-testing.onrender.com").rstrip("/")
        self.browser_name = (browser or self.config.get("browser", "chrome")).lower()
        self.is_headless = headless if headless is not None else self.config.get("headless", False)
        tmo = self.config.get("timeouts", {})
        self.page_load_timeout = tmo.get("page_load", 90)
        self.element_timeout = tmo.get("element", 25)
        self.driver = None

    def init_driver(self):
        """Khởi tạo trình duyệt WebDriver tương ứng."""
        if self.browser_name == "chrome":
            opts = webdriver.ChromeOptions()
            if self.is_headless:
                opts.add_argument("--headless=new")
            opts.add_argument("--window-size=1366,900")
            self.driver = webdriver.Chrome(options=opts)
        elif self.browser_name == "firefox":
            opts = webdriver.FirefoxOptions()
            if self.is_headless:
                opts.add_argument("-headless")
            self.driver = webdriver.Firefox(options=opts)
        elif self.browser_name == "edge":
            opts = webdriver.EdgeOptions()
            if self.is_headless:
                opts.add_argument("--headless=new")
            opts.add_argument("--window-size=1366,900")
            self.driver = webdriver.Edge(options=opts)
        else:
            raise ValueError(f"Unsupported browser: {self.browser_name} (chrome/firefox/edge)")

        self.driver.set_page_load_timeout(self.page_load_timeout)
        return self.driver

    def reset_session(self):
        """Xóa cookie và bộ nhớ trình duyệt để mỗi test case hoàn toàn độc lập."""
        if not self.driver:
            return
        try:
            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        except Exception:
            pass

    def quit_driver(self):
        """Đóng toàn bộ phiên trình duyệt."""
        if self.driver:
            self.driver.quit()
            self.driver = None

