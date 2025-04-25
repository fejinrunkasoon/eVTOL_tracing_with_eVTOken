import socket
import threading

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.bind(('localhost',12345))
server_socket.listen(1)

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect(('localhost',12345))

def send_message(sock,message):
    sock.sendall((message +"\n").encode("utf-8"))

def receive_message(sock):
    data =b""
    while b"\n" not in data:
        chunk =sock.recv(1024)
        if not chunk:
            break
        data +=chunk
    return data.decode("utf-8").strip()

def server():
    conn,addr=server_socket.accept()
    print("Server received:",receive_message(conn))
    print("Server received:",receive_message(conn))
    
def client():
    send_message(client_socket,"Hello")
    send_message(client_socket,"World")
    
threading.Thread(target=server).start()
client()
    
