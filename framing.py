import struct
import socket
import threading 

def send_message(sock,message):#客户端
    message_bytes =message.encode('utf-8')#utf-8编码为二进制字节流
    length_prefix = struct.pack('!I',len(message_bytes))#添加4字节长度前缀（大端字节序）
    sock.sendall(length_prefix + message_bytes)#发送数据（长度前缀 + 消息内容）
    
def receive_message(sock):
    length_prefix =sock.rev(4)
    if not length_prefix:
        return None
    message_length = struct.unpack('!I',length_prefix)[0]
    message_bytes =sock.recv(message_length)
    return message_bytes.decode('utf-8')

server_socket =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.bind(('localhost',12345))
server_socket.listen(1)

client_socket =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect(('localhost',12345))

def server():
    conn, addr = server_socket.accept()
    print("Server received:",receive_message(conn))
    print("Server received:",receive_message(conn))
    
def client():
    send_message(client_socket,"Hello")
    send_message(client_socket,"World")
    
threading.Thread(target=server).start()
client()