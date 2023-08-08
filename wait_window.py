import aux_functions
from driver_init import BrowserDriver


class WindowLoader:
    def __init__(self):
        self.driver = BrowserDriver().browser
        self.aux_func = aux_functions.AuxFunc()

    def load_window(self, target_window_path: str, window_anchor_xpath: str):
        """ Open window by URL
            window_path - target window url
            window_anchor_xpath - xpath that's need to wait to know that window is loaded"""
        self.driver.get(target_window_path)
        while not self._check_window_status(window_anchor_xpath):
            self.driver.get(target_window_path)

    def _check_window_status(self, window_anchor_xpath: str) -> bool:
        """Returns true if target window loaded (by checking element presence on target window)"""
        if not self.aux_func.wait_element_load(xpath=window_anchor_xpath):
            return False
        return True


class WindowLoaderByClick(WindowLoader):
    """Loads window by clicking on button (because URL undefined)"""

    def load_window(self, target_window_path: str, window_anchor_xpath: str):
        """ Open window by URL
            window_path - target button xpath to load window
            window_anchor_xpath - xpath that's need to wait to know that window is loaded"""
        current_window_url = self.driver.current_url
        self.aux_func.try_click(target_window_path)
        while not self._check_window_status(window_anchor_xpath):
            self.driver.get(current_window_url)
            self.aux_func.try_click(target_window_path)
