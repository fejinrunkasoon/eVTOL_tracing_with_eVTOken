from flask import Flask,render_template
from datetime import datetime
from flask import request

app = Flask(__name__)

# @app.route('/')#访问首页,输入http://127.0.0.1:5000跳转home
@app.route('/home')
def home():
    today=datetime.now().strftime('%Y-%m-%d')
    return render_template('home.html',name='huangsi',date=today)

@app.route('/')#访问首页,输入http://127.0.0.1:5000跳转about
@app.route('/about')
def about():
    return render_template('about.html')

# @app.route('/')#访问首页,输入http://127.0.0.1:5000跳转contact
@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        lname =request.form.get('lname')#这里get对应html中的name属性
        fname =request.form.get('fname')#这里get对应html中的name属性
        print(f"my name is {fname} {lname}")
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True)