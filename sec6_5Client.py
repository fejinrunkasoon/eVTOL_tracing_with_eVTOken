import socket
import ssl

# 客户端配置
HOST = '127.0.0.1'  # 服务端地址
PORT = 8443  # 服务端监听的端口
CERT_FILE = 'certificate.pem'  # 服务端自签名证书路径

# 创建 TCP 套接字并使用 SSL 上下文包装
ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_context.load_verify_locations(CERT_FILE)  # 加载服务端自签名证书

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_client_socket = ssl_context.wrap_socket(client_socket, server_hostname=HOST)

try:
    # 连接到服务端
    ssl_client_socket.connect((HOST, PORT))
    print("成功连接到 TLS 服务端")
    
    # 向服务端发送消息
    ssl_client_socket.sendall(b"Hello from TLS client!")
    
    # 接收服务端响应
    response = ssl_client_socket.recv(1024).decode('utf-8')
    print(f"收到服务端响应: {response}")
finally:
    ssl_client_socket.close()



