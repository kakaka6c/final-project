import json
import codecs

json_string = '{"value1":"\(5 x^{3} y\).","value2":"\(3 x^{3} y\).","value3":"\(4 x^{3} y\).","value4":"\(10 x^{3} y\)."}'

# Sử dụng codecs.decode() để xử lý chuỗi trước khi phân tích nó thành JSON
decoded_string = codecs.decode(json_string, 'unicode_escape')

print(decoded_string)
# Phân tích chuỗi JSON
data = json.loads(decoded_string)

# In ra dữ liệu phân tích
print(data)