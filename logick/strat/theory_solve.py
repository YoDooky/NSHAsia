import sys
import time
from typing import Union

from playsound import playsound
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from config import MUSIC_FILE_PATH
from driver_init import driver
from aux_functions import AuxFunc
from exceptions import TheoryNotChanges
from log import print_log
from web.xpaths import XpathResolver
from logick.aux_funcs import RandomDelay


class TheoryStrategy:
    MAX_PAGE_LOAD = 10  # maximum attempts to check if page the same

    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.same_page_counter = 0
        self.theory_click_counter = 0
        self.next_theory_button = XpathResolver.next_theory()
        self.last_page_src = None

    def main(self):
        """Skips all theory"""
        print_log('--> Прокликиваю теорию')

        # try to skip pdf if it exists
        skip_pdf = PdfSkipper()
        skip_pdf()

        # skip general theory
        while AuxFunc().try_click(xpath=self.next_theory_button, try_numb=3, window_numb=1):
            self._click_theory()
        AuxFunc().try_click(xpath=XpathResolver.goto_quiz_button(), try_numb=8)
        time.sleep(5)
        AuxFunc().try_click(xpath=XpathResolver.start_button(), try_numb=8)
        time.sleep(5)
        AuxFunc().try_click(xpath=XpathResolver.continue_button(), try_numb=8, window_numb=1)
        time.sleep(5)

    def _click_theory(self):
        current_page_src = driver.page_source
        # check if page the same
        if self._has_same_page(current_page_src=current_page_src, last_page_src=self.last_page_src):
            raise TheoryNotChanges
        self.last_page_src = current_page_src
        time.sleep(RandomDelay.get_theory_delay())
        sys.stdout.write('\r' + f"Количество успешных кликов: {self.theory_click_counter}")  # print on one line
        sys.stdout.flush()

    def _has_same_page(self, current_page_src: str, last_page_src: str):
        """Checks if page src has been changed since 10 attempts"""
        if self.same_page_counter >= self.MAX_PAGE_LOAD:
            return True
        if last_page_src == current_page_src:
            self.same_page_counter += 1
        else:
            self.theory_click_counter += 1  # increase theory click counter because page has been changed
            self.same_page_counter = 0
        return False


class TheoryStrategyA(TheoryStrategy):
    """Solving theory where is standart window"""


class TheoryStrategyB:
    """Solving theory where is only video"""

    def __init__(self):
        self.theory_click_counter = 0

    def main(self):
        for i in range(10):
            try:
                # self._focus()
                self._set_playback_speed()
                self._mute_sound()
                self._play_video()
                self._wait_video_ending()
                return
            except Exception as ex:
                print_log(
                    message=f'\n[ERR]{ex}'
                            f'-> Не могу запустить видео, пробую еще раз',
                    silent=True
                )
                continue
        playsound(MUSIC_FILE_PATH)
        print_log('[ERR] Не могу пропустить видео')
        input('-> Запусти видео, подожди его окончания и нажми Enter')

    def _wait_video_ending(self):
        """Waits until video will end"""
        print_log('-> Жду окончания видео')
        time_left = 10
        while time_left:
            # self._focus()
            progress_text = self._get_progress()
            time_left = self._get_time_left(progress_text)
            time.sleep(int(time_left / 10))

    # @staticmethod
    # def _focus():
    #     """Focus on page"""
    #     driver.switch_to.window(driver.window_handles[-1])
    #     actions = ActionChains(driver)
    #     actions.move_by_offset(0, 0).click().perform()

    @staticmethod
    def _show_control():
        """Show auto hiding player control panel"""
        mp_mask = '//*[@id="mediaPlayer"]'
        mp_element = driver.find_element(By.XPATH, mp_mask)
        ActionChains(driver).move_to_element(mp_element).perform()

    def _set_playback_speed(self):
        """Sets playback speed x2"""
        self._show_control()
        # open playback speed menu
        playback_speed_menu_mask = '//*[@id="playbackSpeed"]'
        driver.find_element(By.XPATH, playback_speed_menu_mask).click()
        # choose x2 speed
        playback_speed_x2_mask = '//ul[@class="playback_speed_list"]/li'
        driver.find_elements(By.XPATH, playback_speed_x2_mask)[-1].click()

    def _mute_sound(self):
        """Mute sound"""
        self._show_control()
        # turn off sound
        sound_button_mask = '//div[@id="volumePickerVolumeIcon"]'
        AuxFunc().try_click(sound_button_mask)

    def _play_video(self):
        """Start video playback"""
        self._show_control()
        # play video
        play_button_mask = '//div[@class="play_pause"]'
        AuxFunc().try_click(play_button_mask)

    def _get_progress(self) -> str:
        """Returns progress bar text"""
        self._show_control()
        progress_bar_mask = '//div[@id="timeInformation"]'
        return AuxFunc().try_get_text(xpath=progress_bar_mask, amount=1)

    @staticmethod
    def _get_time_left(progress_text: str) -> int:
        """Returns time left"""

        def time_to_second(time_str: str) -> int:
            """Returns time in seconds"""
            hours, minutes, seconds = map(int, time_str.split(':'))
            return hours * 3600 + minutes * 60 + seconds

        video_timer = time_to_second(progress_text.split('/')[0].strip())
        overall_time = time_to_second(progress_text.split('/')[-1].strip())
        return overall_time - video_timer


class TheorySolveStrategy:
    """Strategy for theory solving"""

    def __init__(self, strategy: TheoryStrategy):
        self.strategy = strategy

    def do_work(self):
        self.strategy.main()


class PdfSkipper:
    """Class for skipping pdf files"""

    def __call__(self, *args, **kwargs):
        """Skip all pdf pages"""
        print_log(message='Пробую скипнуть pdf, если он есть', silent=True)
        while self.go_next_page():
            if not self.go_next_page():
                break

    @staticmethod
    def get_next_page_button() -> Union[WebElement, None]:
        """Return next pdf page button"""
        next_page_mask = '//*[@class[contains(.,"icon next")]]/..'
        for i in range(3):
            driver.switch_to.window(driver.window_handles[-1])
            iframe = driver.find_element(By.XPATH, '//iframe')
            driver.switch_to.frame(iframe)
            try:
                actions = ActionChains(driver)
                actions.move_by_offset(0, 0).click().perform()
                button = driver.find_element(By.XPATH, next_page_mask)
                return button
            except Exception as ex:
                time.sleep(1)
                continue

    def go_next_page(self) -> bool:
        """Go next pdf page"""
        next_button = self.get_next_page_button()
        if next_button is None:
            return False
        if next_button.get_attribute('disabled'):
            return False
        next_button.click()
        time.sleep(1)
        return True
