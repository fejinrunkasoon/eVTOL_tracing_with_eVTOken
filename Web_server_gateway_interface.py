from wsgiref.simple_server import make_server#服务端
from pprint import pformat

def app(environ, start_response):
    # headers =[('Content-Type','text/plain; charset=utf-8')]#WSGI 是 Python Web 应用与服务器之间的通用接口标准，它规定 start_response 的第二个参数必须是一个由 (header_name, header_value) 元组组成的列表。
    # start_response('200 OK', headers)
    headers = {'Content-Type': 'text/plain; charset=utf-8'}
    start_response('200 OK', list(headers.items()))
    yield 'Here is the WSGI environment:\r\n\r\n'.encode('utf-8')
    yield pformat(environ).encode('utf-8')
    
if __name__ == '__main__':
    httpd = make_server('',8000,app)#借助wsgiref模块创建一个WSGI服务器，浏览器打开http://0.0.0.0:8000/
    host, port =httpd.socket.getsockname()
    print(f"Serving on http://{host}:{port}/")
    httpd.serve_forever()