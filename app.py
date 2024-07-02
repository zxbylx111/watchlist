from flask import Flask, url_for
from markupsafe import escape

app = Flask(__name__)


# @app.route('/home')
# def hello1():
#     return 'Welcome to My Watchlist!'


@app.route('/')
@app.route('/index')
@app.route('/home')
def hello():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'


@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'


@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请访问http://localhost:5000/test 后在命令行窗口查看输出的URL
    print(url_for('hello'))
    print(url_for('user_page', name='Totoro'))
    print(url_for('user_page', name='Peter'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for', num=2)) #输出/test?num=2
    return 'Test page'
