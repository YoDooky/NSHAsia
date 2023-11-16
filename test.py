import time

from playsound import playsound
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from aux_functions import AuxFunc
from config import MUSIC_FILE_PATH
from driver_init import driver
from log import print_log


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


# TheoryStrategyB().main()
