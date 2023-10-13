def is_page_src():
    compare_counter = 1

    def compare_str(last_str: str, current_str: str):
        nonlocal compare_counter
        if last_str == current_str:
            compare_counter += 1
            return
        compare_counter = 0

    return compare_str


pg_src = is_page_src()
for i in range(10):
    str1 = 'test2'
    str2 = 'test2'
    pg_src(last_str=str2, current_str=str1)
