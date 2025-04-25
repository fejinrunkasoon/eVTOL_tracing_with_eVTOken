import socket
import argparse

def recvall(sock, length):
    data = b''
    while len(data )< length:
        more =sock.recv(length -len(data))
        if not more:
            raise EOFError(f'Expected {length} bytes but only received {len(data)} bytes before the socket closed')
        data += more
        
    return data

def server(interface,port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)#设置套接字选项
    sock.bind((interface,port))
    sock.listen(1)#Passive socket
    print(f"Listening at {sock.getsockname()}")    
    while True:
        print("waitinng to accept a new connection")
        sc,sockname=sock.accept()
        print(f"we have accepted a connection from {sockname}")
        print(f"socket name:{sc.getsockname()}")
        print(f"socket peer:{sc.getpeername()}")
        message = recvall(sc,16)
        print(f"incoming sixteen-octet message:{repr(message)}")
        sc.sendall(b'Farewell,client')  
        sc.close()
        print("Reply sent,socket closed")
        
def client(host,port):
    sock =socket.socket(socket.AF_INET,socket.SOCK_STREAM)#sock_stream表示TCP，sock_dgram表示UDP
    bytecount =(bytecount +15)
    sock.connect((host,port))
    print(f"client has been assigned socket name {sock.getsockname()}")
    sock.sendall(b"Hi,server")
    reply = recvall(sock,16)
    print(f"The server said {repr(reply)}")
    sock.close()
    
if __name__ == '__main__':
    choices = {'client':client,'server':server}
    parser = argparse.ArgumentParser(description='Send and receive over TCP')
    parser.add_argument('role',choices=choices,help='which role to play')
    parser.add_argument('host',help='interface the server listen at;'"host the client send to")
    parser.add_argument('-p',metavar='PORT',type=int,default=1060,help='TCP port (default 1060)')
    args = parser.parse_args()
    function =choices[args.role]
    function(args.host,args.p)    