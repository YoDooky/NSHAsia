# from selenium.webdriver.common.by import By
#
# from driver_init import driver
# from web import XpathResolver, CourseWebData
#
# driver.get('https://pnsh.ispringlearn.ru/content/info/13018')
# courses = CourseWebData().get_courses()
#
# for i in range(len(courses)):
#     try:
#         course_link = CourseWebData().get_courses()[i]
#         driver.switch_to.window(driver.window_handles[0])
#         course_link.click()
#         driver.get('https://pnsh.ispringlearn.ru/content/info/13018')
#     except:
#         pass
# driver.quit()
# driver.close()
from typing import List


def get_courses_from_user() -> List[int]:
    """Return user selected courses"""
    user_input = input('\nВведи номера курсов для решения через запятую, либо'
                       'через тире если нужно решить несколько подряд:')
    str_mod = user_input.split(',')
    str_comma = [int(s.strip()) for s in str_mod if '-' not in s]

    def get_str_dash(string_input: List[str]) -> List[int]:
        str_dash = []
        for num in string_input:
            if '-' not in num:
                continue
            str_dash.extend(
                [i for i in range(int(num.split('-')[0].strip()),
                                  int(num.split('-')[1].strip()) + 1)]
            )
        return str_dash

    str_comma.extend(get_str_dash(str_mod))
    str_comma.sort()
    return str_comma


nums = get_courses_from_user()
print(nums)
