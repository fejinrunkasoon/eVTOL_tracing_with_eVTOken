import random
import argparse,socket
from datetime import datetime
import sys

MAX_BYTES = 65535 #可接受最大字节数

def server(interface,port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)#IPv4和UDP
    # sock.bind(('127.0.0.1',port))
    sock.bind((interface,port))#socket绑定对应接口和端口号
    print(f'Listening at {sock.getsockname()}')
    while True:
        data, address = sock.recvfrom(MAX_BYTES)#服务器返回recvfrom(),等待下一个客户端请求，这是个循环过程，直到服务器被关闭
        # if random.random() < 0.9: #丢包的概率，概率越大丢的越多
        #     print(f'Pretending to drop packet from {address}')
        #     continue
        text = data.decode('ascii')
        print(f'The client at {address} says({text!r})')
        # message = f'Your data was {len(data)} bytes long'
        # sock.sendto(message.encode('ascii'),address)
        data = text.encode('ascii')#编码格式采用"ascii"
        sock.sendto(data,address)#指定客户端的IP地址和端口号，以便服务器知道将数据发送到哪里
        
def client(hostname,port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)#指定socket.AF_INET:IPv4,socket.SOCK_DGRAM:UDP协议
    # hostname = sys.argv[2]
    # sock.connect((hostname,port))
    # print(f'Client socket name is {sock.getsockname()}')
    
    # delay = 0.1
    # text = 'This is another message'
    # data = text.encode('ascii')
    # while True:
    #     sock.send(data)
    #     print(f'Waiting up to {delay} seconds for a replay')
    #     sock.settimeout(delay)
    #     try:
    #         data = sock.recv(MAX_BYTES)
    #     except socket.timeout as exc:
    #         delay *= 2
    #         if delay >0.1:
    #             raise RuntimeError('I think the server is down') from exc
    #         else:
    #             break 
            
    # print(f'The server says {data.decode("ascii")}')
    
    text =f'The time is {datetime.now()}'
    data = text.encode('ascii')
    sock.sendto(data,('127.0.0.1',port))#指定服务器的IP地址和端口号
    print(f'The OS assigned me the address {sock.getsockname()}')
    data, address = sock.recvfrom(MAX_BYTES)#等待接受来自服务器的响应数据
    text =data.decode('ascii')
    print(f'The server {address!r} replied {text!r}')
        
if __name__ =='__main__':
    choices = {'client': client,'server': server}#选择在终端运行client/server
    parser =argparse.ArgumentParser(description = 'Send and receive UDP locally,''pretending packets are often dropped')
    parser.add_argument('role',choices=choices,help='which role to play')#选择在终端运行client/server
    parser.add_argument('host',help='interface the server listens at;'' host the client sends to')
    parser.add_argument('-p',metavar='PORT',type=int,default=1060,help='UDP port (default 1060)')
    args =parser.parse_args()
    function =choices[args.role]
    function(args.host,args.p)
        