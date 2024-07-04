from flask import Flask, url_for, render_template, flash, redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from watchlist import app, db
from watchlist.models import User, Movie


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Your movie has been added.')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请访问http://localhost:5000/test 后在命令行窗口查看输出的URL
    print(url_for('hello'))
    print(url_for('user_page', name='Totoro'))
    print(url_for('user_page', name='Peter'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for', num=2)) #输出/test?num=2
    return 'Test page'


@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html'), 404


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item Updated.')
        return redirect(url_for('index'))
    return render_template('edit.html', movie=movie)


# @app.route('/movie/delete/<int:movie_id>', methods=['POST'])
# def delete(movie_id):
#     click(movie_id)
#     movie = Movie.query.get_or_404(movie_id)
#     db.session.delete(movie)
#     db.session.commit()
#     flash('Item Deleted.')
#     return redirect(url_for('index'))

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))
        flash('Invalid username or password')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')