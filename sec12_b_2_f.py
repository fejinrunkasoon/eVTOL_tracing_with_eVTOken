from flask import Flask,render_template,request
from flask_mysqldb import MySQL

app = Flask(__name__)

# name = 'lppx'
# movies =[
#     {'title':'M1','year':'1998'},
#     {'title':'M2','year':'1998'},
#     {'title':'M3','year':'1998'},
#     {'title':'M4','year':'1998'},
#     {'title':'M5','year':'1998'},
#     {'title':'M6','year':'1998'},
#     {'title':'M7','year':'1998'},
#     {'title':'M8','year':'1998'}
# ]

# @app.route('/')
# def home():
#     return render_template('movies.html',name =name, movies =movies)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='yeP:@gun8'
app.config['MYSQL_DB'] = 'four'

mysql = MySQL(app)

#查询
@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, name, age FROM users')
    users = cursor.fetchall()
    cursor.close()
    return render_template('index.html', users=users)

@app.route('/add',methods = ['GET','POST'])
def add():
    if request.method == 'POST':
       
        name = request.form.get('name')
        age = request.form.get('age')

        print(f"id={id},name={name},age={age}")
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (name, age) VALUES (%s,%s)',(name,age))
        mysql.connection.commit()
        cursor.close()
    return render_template('add.html')
 
@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/delete',methods = ['GET','POST'])
def delete():
    if request.method == 'POST':
    
        name = request.form.get('name')#从html拿数据
        if name:#确认name存在
            cursor = mysql.connection.cursor()
            cursor.execute('DELETE FROM users WHERE name = %s',(name,))
            mysql.connection.commit()
            cursor.close()
    return render_template('delete.html')
    
# @app.route('/')
# def home():
#     return render_template('movies.html',name =name, movies =movies)

if __name__ == '__main__':
    app.run(debug=True)