#客户端

# import urllib.request#处理URL和HTTP需要手动处理request header/参数

# url = "http://baidu.com"
# with urllib.request.urlopen(url) as response:
#     html = response.read().decode('utf-8')
#     print(html)
#     print(response.status)

import requests#简化了HTTP请求的发送和处理
url = "http://baidu.com"
response =requests.get(url)
print(response.text)