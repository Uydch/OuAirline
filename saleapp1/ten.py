from itertools import product

def generate_cases(s):
    # Tạo danh sách các ký tự với chữ hoa và chữ thường
    options = [(char.lower(), char.upper()) if char != ' ' else (' ',) for char in s]
    # Tạo tất cả các kết hợp
    combinations = product(*options)
    # Chuyển đổi các kết hợp thành chuỗi
    return [''.join(combination) for combination in combinations]

# Sử dụng hàm
cases = generate_cases("tran thi minh trang")
for case in cases:
    print(case)