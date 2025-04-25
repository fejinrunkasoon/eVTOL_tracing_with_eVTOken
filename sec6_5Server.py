import socket
import ssl

# 服务端配置
HOST = '127.0.0.1'  # 本地地址
PORT = 8443  # 监听的端口
CERT_FILE = 'certificate.pem'  # 自签名证书路径
KEY_FILE = 'private_key.pem'  # 私钥路径

# 创建 TCP 套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

# 使用 SSL 上下文包装套接字
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
ssl_server_socket = ssl_context.wrap_socket(server_socket, server_side=True)

print(f"TLS 服务端正在运行，地址: {HOST}:{PORT}")

try:
    # 接受客户端连接
    conn, addr = ssl_server_socket.accept()
    print(f"与客户端 {addr} 建立连接")
    
    # 接收客户端数据
    data = conn.recv(1024).decode('utf-8')
    print(f"收到客户端消息: {data}")
    
    # 向客户端发送响应
    conn.sendall(b"Hello from TLS server!")
    
    conn.close()
except Exception as e:
    print(f"服务端错误: {e}")
finally:
    ssl_server_socket.close()


