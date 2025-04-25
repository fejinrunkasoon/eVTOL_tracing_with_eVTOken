# from urllib.parse import urlparse
# from urllib.parse import urlunparse
from urllib.parse import urljoin

# url ='https://music.163.com/#/my/m/music/playlist?id=957965961'
# parse =urlparse(url)

# print(parse.scheme)
# print(parse.netloc)
# print(parse.path)
# print(parse.params)
# print(parse.query)
# print(parse.fragment)

# print(parse.hostname)
# print(parse.port)
# print(parse.username)
# print(parse.password)

# components = (
#     'https',
#     'example.com:8080',
#     '/path/file.html',
#     'param',
#     'query=arg',
#     'fragment'
# )

# new_url = urlunparse(components)
# print(new_url)

# base_url ='https://example.com/folder/'
# relative_url = 'page.html'
# absolute_url =urljoin(base_url,relative_url)
# print(absolute_url)
# print(urljoin('http://www.example.com/dir/','subpage.html'))#http://www.example.com/dir/subpage.html
# print(urljoin('http://www.example.com/dir/subdir/','../page.html'))#http://www.example.com/dir/page.html
# print(urljoin('http://www.example.com/dir/page.html','/newpath'))#http://www.example.com/newpath

from flask import Flask,render_template
app =Flask(__name__)

@app.route('/')
def home():
    return render_template('fragment.html')

if __name__ == "__main__":
    app.run(debug=True)