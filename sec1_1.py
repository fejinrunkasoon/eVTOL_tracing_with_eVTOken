# conda activate pythonNetwork

import requests
import json
import re

AK = 'fL7V36EwfdN96ps0mnSJRcKY2bHdj13R'
address ='广东省东莞市石排镇东园大道2号'
url = 'http://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak={}&callback=showLocation'.format(address,AK)
res = requests.get(url)
print(res.text)
results = json.loads(re.findall(r'\((.*?)\)',res.text)[0])
print('\n')
print('location is ',results['result']['location'])



