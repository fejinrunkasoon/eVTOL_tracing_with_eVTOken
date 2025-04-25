import sys
import argparse, socket

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (length, len(data)))
        data += more
    return data

def server(interface, port,bytecount):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((interface, port))
    sock.listen(1)
    print('Listening at', sock.getsockname())
    while True:
        sc, sockname = sock.accept()
        print('We have accepted a connection from', sockname)
        n=0
        while True:
            data =sc.recv(1024)
            if not data:
                break
            output = data.decode('ascii').upper().encode('ascii')
            sc.sendall(output) #send it back uppercase
            n += len(data)
            print('\r %d bytes processed so far' % (n,), end=' ')
            sys.stdout.flush()
        print()
        sc.close()  
        print('Reply sent,socket closed')
        
def client(host, port,bytecount):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bytecount += 15
    message = b'capitailize this'
    print('Sending',bytecount,'bytes of data, in chunks of 16 bytes')
    sock.connect((host, port))
    
    sent = 0
    while sent < bytecount:
        sock.sendall(message)
        sent += len(message)
        print('\r %d bytes sent' % (sent,), end=' ')
        sys.stdout.flush()
        
    print() 
    sock.shutdown(socket.SHUT_WR)
    
    print('Receiving all the data the server sends back')   
    
    received = 0
    while True:
        data = sock.recv(42)
        if not received:
            print('The first data received says', repr(data))
        if not data:
            break# 中断
        received += len(data)
        print('\r %d bytes received' % (received,), end=' ')
    print()
    sock.close()
    # sock.connect((host, port))
    # print('Client has been assigned socket name', sock.getsockname())
    # sock.sendall(b'Hi there, server')
    # reply = recvall(sock, 16)
    # print('The server said', repr(reply))
    # sock.close()

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive over TCP')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('host', help='interface the server listens at;'
                        ' host the client sends to')
    parser.add_argument('bytecount', type=int,nargs='?',default=16, help='number of bytes for client to send')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p,args.bytecount)
