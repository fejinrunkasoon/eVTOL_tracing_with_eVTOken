# import http.client
import json
import re
import urllib.parse
import socket

AK = 'fL7V36EwfdN96ps0mnSJRcKY2bHdj13R'#申请个人的百度地图API 的key

def geocode(address):
    encoded_address= urllib.parse.quote(address)#将中文地址转换成url编码格式
    request_line = f'GET /geocoding/v3/?address={encoded_address}&output=json&ak={AK}&callback=showLocation HTTP/1.1\r\n'#GET请求行
    headers = ('Host: api.map.baidu.com\r\n'
               'Connection:close\r\n'
               '\r\n'
               )
    
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s: #建立一个socket连接，AF_INET表示使用IPv4协议，SOCKET_STREAM表示使用TCP协议
        s.connect(('api.map.baidu.com',80))
        s.sendall((request_line + headers).encode("utf-8"))
    
        response = b""#定义一个空的字节串bytes(),用于以下接受data数据，循环叠加成独立的字节文本
        while True: #While循环，用s.recv()接收数据,最大可达4096字节，直到没有data传入跳出循环
            data =s.recv(4096)
            if not data:
                break
            response += data#字节串拼接
    
    response_text = response.decode('utf-8')#解码经过socket接收的完整字节文本，转换成utf-8编码格式的字符串
    print(response_text)
    
    results = json.loads(re.findall(r'\((.*?)\)', response_text)[0])
    #正则表达式\(和\)对应左右括号(),(.*?)找到所有被()包裹的内容。其中，非贪婪模式 ? 确保遇到第一个右括号 ) 就停止匹配，避免跨括号匹配。
    #[0] 获取列表中的第一个元素。json.loads()将json格式转化为python字典格式
    print('\n')
    print('location is ', results['result']['location'])
    
if __name__ == '__main__':
    hostname = 'www.baidu.com'#183.240.99.169
    addr = socket.gethostbyname(hostname)
    print(f'The IP address of {hostname} is {addr}')
    # geocode('广东省东莞市石排镇东园大道2号')
