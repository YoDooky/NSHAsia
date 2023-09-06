import re

text = "В этой строке есть 123 ифцвфцв 456."
digits = re.findall(r'\d+', text)
print(digits)