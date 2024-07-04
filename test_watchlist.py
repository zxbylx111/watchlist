
import pytest
from watchlist import app, db
from watchlist.models import Movie, User
from watchlist.commands import forge, initdb


@pytest.fixture(scope='function')
def database():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
    )
    # 创建数据库和表
    app.app_context().push()
    db.create_all()
    user = User(name='Test', username='test')
    user.set_password('123')
    movie = Movie(title='Test Movie Title', year='2019')
    db.session.add_all([user, movie])
    db.session.commit()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def login():
    app.app_context().push()
    app.test_client().post('/login', data=dict(
        username='test',
        password='123'
    ), follow_redirects=True)


@pytest.fixture(scope='function')
def runner():
    app.app_context().push()
    runner = app.test_cli_runner()
    return runner


class TestWatchlist:
    def test_app_exists(self, database):
        assert app is not None

    def test_app_is_testing(self, database):
        assert app.config['TESTING'] is True

    def test_404_page(self, database):
        response = app.test_client().get('/nothing')
        data = response.get_data(as_text=True)
        assert response.status_code == 404
        assert 'Page Not Found - 404' in data
        assert 'Go Back' in data

    def test_index_page(self, database):
        response = app.test_client().get('/')
        data = response.get_data(as_text=True)
        assert response.status_code == 200
        assert 'Test\'s Watchlist' in data
        assert 'Test Movie Title' in data

    def test_create_item(self, database, login):
        response = app.test_client().post('/', data=dict(
            title='New Movie',
            year='2019',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Your movie has been added.' in data
        assert 'New Movie' in data

        response = app.test_client().post('/', data=dict(
            title='',
            year='2019',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Your movie has been added.' not in data
        assert 'Invalid input.' in data

        # 电影年份为空
        response = app.test_client().post('/', data=dict(
            title='New Movie',
            year='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Your movie has been added.' not in data
        assert 'Invalid input.' in data

    def test_update_item(self, database, login):
        response = app.test_client().get('/movie/edit/1')
        data = response.get_data(as_text=True)
        assert 'Edit item' in data
        assert 'Test Movie Title' in data
        assert '2019' in data

        # 测试更新条目操作
        response = app.test_client().post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Item Updated.' in data
        assert 'New Movie Edited' in data
        #
        response = app.test_client().post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Item Updated.' not in data
        assert 'Invalid input.' in data
        #
        response = app.test_client().post('/movie/edit/1', data=dict(
            title='New Movie Edited Again',
            year=''
        ), follow_redirects=True)
        assert 'Item Updated.' not in data
        assert 'Invalid input.' in data
        assert 'New Movie Edited Again' not in data

    def test_delete_item(self, database, login):
        response = app.test_client().post('movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Item deleted.' in data
        assert 'Test Movie Title' not in data

    # 测试登录、登出和认证保护功能
    def test_login_protect(self, database):
        response = app.test_client().get('/')
        data = response.get_data(as_text=True)
        assert 'Logout' not in data
        assert 'Settings' not in data
        assert '<form method="post">' not in data
        assert 'Delete' not in data
        assert 'Edit' not in data

    def test_login(self, database):
        response = app.test_client().post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Login success.' in data
        assert 'Logout' in data
        assert 'Settings' in data
        assert '<form method="post">' in data
        assert 'Delete' in data
        assert 'Edit' in data

        # 测试使用错误密码登录
        response = app.test_client().post('/login', data=dict(
            username='test',
            password='<PASSWORD>'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Login success.' not in data
        assert 'Invalid username or password' in data

        # 测试使用空用户名登录
        response = app.test_client().post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Login success.' not in data
        assert 'Invalid input.' in data

        # 测试使用空密码登录
        response = app.test_client().post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Login success.' not in data
        assert 'Invalid input.' in data

    def test_logout(self, database, login):
        response = app.test_client().get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Goodbye.' in data
        assert 'Logout' not in data
        assert 'Settings' not in data
        assert '<form method="post">' not in data
        assert 'Delete' not in data
        assert 'Edit' not in data

    def test_settings(self, database, login):
        response = app.test_client().get('/settings')
        data = response.get_data(as_text=True)
        assert 'Settings' in data
        assert 'Your Name' in data

        # 测试更新设置
        response = app.test_client().post('/settings', data=dict(
            name='xinbo'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Settings updated.' in data
        assert 'xinbo' in data

        response = app.test_client().post('/settings', data=dict(
            name=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'Settings updated.' not in data
        assert 'Invalid input.' in data

    # 测试自定义命令行
    def test_forge_command(self, runner):
        result = runner.invoke(forge)
        assert 'Done.' in result.output
        assert Movie.query.count() != 0

    def test_initdb_command(self, runner):
        result = runner.invoke(initdb)
        assert 'Initialized database.' in result.output

    def test_admin_command(self, runner):
        db.drop_all()
        db.create_all()
        result = runner.invoke(args=['admin', '--username', 'zxb', '--password', '123456'])
        assert 'Creating new user...' in result.output
        assert 'Done.' in result.output
        assert User.query.count() == 1
        assert User.query.first().username == 'zxb'
        assert User.query.first().validate_password('123456')

    def test_admin_command_update(self, runner):
        result = runner.invoke(args=['admin', '--username', 'peter', '--password', '456'])
        assert 'Updating user...' in result.output
        assert 'Done.' in result.output
        assert User.query.count() == 1
        assert User.query.first().username == 'peter'
        assert User.query.first().validate_password('456')
