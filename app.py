from flask import Flask, url_for, render_template
from markupsafe import escape

app = Flask(__name__)


# @app.route('/home')
# def hello1():
#     return 'Welcome to My Watchlist!'
name = 'zxb'
movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]


@app.route('/')
def index():
    return render_template('index.html', name=name, movies=movies)


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
