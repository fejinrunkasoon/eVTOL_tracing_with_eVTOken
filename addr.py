# import socket
# import sys
# import argparse

# def conn_to(hostname_or_ip):
#     try:
#         infolist =socket.getaddrinfo(
#             hostname_or_ip,"www",0,socket.SOCK_STREAM,0,
#             socket.AI_ADDRCONFIG | socket.AI_V4MAPPED | socket.AI_CANONNAME
#             #AI_ADDRCONFIG:仅限于符合IPv6的配置,socket.AI_V4MAPPED:如果没有IPv6地址,则返回IPv4地址解析成IPv6v6,socket.AI_CANONNAME:返回规范名称
#             )
        
#     except socket.gaierror as e:
#         print("Name service failure:",e.args[1])
#         sys.exit(1)
        
#     # info =infolist
#     info =infolist[0]
#     print(infolist)
#     print(info)
#     socket_args = info[0:3]
#     address = info[4]
#     s = socket.socket(*socket_args)
#     try:
#         s.connect(address)
#     except socket.error as e:
#         print("Network failure:",e.args[1])
#     else:
#         print("Success: host",info[3],"is listening on port 80")
        
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Try connecting to port 80')
#     parser.add_argument('hostname',help='hostname that you want to contact')
#     conn_to(parser.parse_args().hostname)

import argparse, dns.resolver

def lookup(name):
    for qtype in 'A','AAAA','CNAME','MX','NS':
        answer =dns.resolver.query(name,qtype,raise_on_no_answer=False)
        if answer.rrset is not None:
            print(answer.rrset)
            
if __name__ =='__main__':
    parser = argparse.ArgumentParser(description = 'Resolve a name using DNS')
    parser.add_argument('name',help='name that you want to look up in DNS')
    lookup(parser.parse_args().name)
        