from selenium.webdriver.common.by import By

from driver_init import driver

driver.get(
    'C:/Users/user/Downloads/%D0%9B%D0%B0%D0%B1%D0%BE%D1%80%D0%B0%D0%BD%D1%82%20%D0%BF%D0%BE%20%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7%D1%83%20%D0%B3%D0%B0%D0%B7%D0%BE%D0%B2%20%D0%B8%20%D0%BF%D1%8B%D0%BB%D0%B8%202%20%D0%BC%D0%BE%D0%B4%D1%83%D0%BB%D1%8C.html')
mask = '//*[@class="choice-view"]'
driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@class="content_frame"]'))
element = driver.find_element(By.XPATH, mask)
try:
    is_disabled = element.get_attribute('disable')
    print(is_disabled)
except Exception as ex:
    driver.quit()
