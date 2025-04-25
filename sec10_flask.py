from flask import Flask, request, jsonify
app = Flask(__name__)

#模拟数据库
books =[
    {"id":0,'title':'A file upon the deep','author':'Vernor vinge','year':1992},
    {"id":1,'title':'The  ones who walk away from omelas','author':'Ursula K.Le Guin','year':1973},
    {"id":2,'title':'Dhalgren','author':'Samuel R.Delany','year':1975}  
]

#GET /books
@app.route('/books', methods=['GET']) #路径为 http://127.0.0.1:5000/books/
def get_books():
    return jsonify({"books":books})

#GET /books/<int:book_id>
@app.route('/books/<int:book_id>', methods=['GET']) #路径为 http://127.0.0.1:5000/books/0
def get_book(book_id):#由于是get请求，可以在网页输入路径直接查询json数据
    book =[book for book in books if book['id'] == book_id]
    if len(book)==0: #确认是否存在该id的book，若无则返回404错误
        return jsonify({"error":"book not found"}),404
    return jsonify({"book":book[0]})

#POST /books
@app.route('/books', methods=['POST']) #路径为 http://127.0.0.1:5000/books
def create_book():
    new_book = { #在Windows powerShell 中运行命令： Invoke-WebRequest -Uri "http://localhost:5000/books" -Method POST -ContentType "application/json" -Body '{"title":"xxx", "author":"xxx", "year":2025}'
        "id": len(books), #id无需手动输入,可以自动生成id
        "title": request.json.get("title"),
        "author": request.json.get("author"),
        "year": request.json.get("year")
    }
    books.append(new_book)
    return jsonify({"book": new_book}), 201

#PUT /books/<int:book_id>
@app.route('/books/<int:book_id>', methods=['PUT']) #路径为 http://127.0.0.1:5000/books/0
def update_book(book_id): # Invoke-WebRequest -Uri "http://localhost:5000/books/3" -Method PUT -ContentType "application/json" -Body '{"title":"hola", "author":"abcdefg", "year":2004}'
    book =[book for book in books if book['id'] == book_id]
    if len(book)==0: #确认是否存在该id的book，若无则返回404错误
        return jsonify({"message":"book not found"}),404
    book[0]['title'] = request.json.get("title", book[0]['title'])
    book[0]['author'] = request.json.get("author", book[0]['author'])
    book[0]['year'] = request.json.get("year", book[0]['year'])
    return jsonify({"book":book[0]})

#DELETE /books/<int:book_id>
@app.route('/books/<int:book_id>', methods=['DELETE']) #路径为 http://127.0.0.1:5000/books/0
def delete_book(book_id): # Invoke-WebRequest -Uri "http://localhost:5000/books/3" -Method DELETE -ContentType "application/json"
    book =[book for book in books if book['id'] == book_id]
    if len(book)==0: #确认是否存在该id的book，若无则返回404错误
        return jsonify({"message":"book not found"}),404
    books.remove(book[0])
    return jsonify({"message":"book deleted"}),200

if __name__ == '__main__':
    app.run(debug=True)