from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from driver_init import driver


def main():
    try:
        driver.switch_to.window(driver.window_handles[-1])
        driver.switch_to.frame(driver.find_element(By.XPATH, '//iframe'))
        new_elements = driver.find_elements(
            By.XPATH,
            '//div[@class="treecontrol treecontrol_with-scroll"]'
            '//div[@class[contains(.,"slide-item-view slide-item-view_with-thumbnail")]]'
        )
        print()
    except Exception as ex:
        driver.quit()


if __name__ == '__main__':
    main()
    driver.quit()
