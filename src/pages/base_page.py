"""BasePage: Lớp cơ sở của toàn bộ các đối tượng trang (Page Objects).
"""
from src.base.validate_helper import ValidateHelper


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.helper = ValidateHelper(driver)

    def get_current_url(self) -> str:
        return self.helper.get_current_url()

