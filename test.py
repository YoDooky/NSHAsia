# import time
#
# from selenium.webdriver import ActionChains
# from selenium.webdriver.common.by import By
#
# from aux_functions import AuxFunc
# from driver_init import driver
#
#
# def get_time_left(time_string: str) -> int:
#     """Returns time left"""
#
#     def time_to_second(time_s: str) -> int:
#         """Returns time in seconds"""
#         hours, minutes, seconds = map(int, time_s.split(':'))
#         return hours * 3600 + minutes * 60 + seconds
#
#     video_timer = time_to_second(time_string.split('/')[0].strip())
#     overall_time = time_to_second(time_string.split('/')[-1].strip())
#     return overall_time - video_timer
#
#
# try:
#     driver.switch_to.window(driver.window_handles[0])
#     actions = ActionChains(driver)
#     actions.move_by_offset(0, 0).click().perform()
#     # open playback speed menu
#     playback_speed_menu_mask = '//*[@id="playbackSpeed"]'
#     driver.find_element(By.XPATH, playback_speed_menu_mask).click()
#     # choose x2 speed
#     playback_speed_x2_mask = '//ul[@class="playback_speed_list"]/li'
#     driver.find_elements(By.XPATH, playback_speed_x2_mask)[-1].click()
#     # turn off sound
#     sound_button_mask = '//div[@id="volumePickerVolumeIcon"]'
#     AuxFunc().try_click(sound_button_mask)
#     # play video
#     play_button_mask = '//div[@class="play_pause"]'
#     AuxFunc().try_click(play_button_mask)
#     # while video timer is not over
#     time_left = 10
#     while time_left:
#         driver.switch_to.window(driver.window_handles[0])
#         actions = ActionChains(driver)
#         actions.move_by_offset(0, 0).click().perform()
#         time.sleep(10)
#         progress_bar_mask = '//div[@id="timeInformation"]'
#         progress_text = AuxFunc().try_get_text(xpath=progress_bar_mask, amount=1)
#         time_left = get_time_left(progress_text)
#
#     driver.quit()
# except Exception as ex:
#     driver.quit()

print(int(1313/2))