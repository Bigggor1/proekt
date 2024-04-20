import datetime

from flask import Flask, render_template, redirect
import requests
from flask_login import LoginManager, login_user, logout_user, login_required
from forms.user import RegisterForm, LoginForm, SearchForm
from data import db_session
from data.users import User

# сервер ставится
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

# создаётся база данных
db_session.global_init("db/blogs.db")


# поиск новостей по списку параметров
def everything(params):
    req = requests.get(f'{params['url']}?'
                       f'apiKey={params['apiKey']}&'
                       f'q={params['q']}&'
                       f'language={params['language']}&'
                       f'sortBy={params['sortBy']}')
    json = req.json()
    return json


# новости для главной страницы по категории
def top_headlines(params):
    req = requests.get(f'{params['url']}?'
                       f'apiKey={params['apiKey']}&'
                       f'country={params['country']}&'
                       f'category={params['category']}')
    json = req.json()
    return json


@app.route('/')
@app.route('/news_main')
def news_main():
    form = SearchForm()
    request_top_headlines = {'apiKey': '162e6651da2c4734b2cfa2d940a47cc5',
                             'url': 'https://newsapi.org/v2/top-headlines',
                             'country': 'ru', 'category': 'general'}
    data = top_headlines(request_top_headlines)
    return render_template('news_main.html', data=data, title='Главная страница', form=form)


@app.route('/news_main/<category>')
def news_main_category(category):
    form = SearchForm()
    request_top_headlines = {'apiKey': '162e6651da2c4734b2cfa2d940a47cc5',
                             'url': 'https://newsapi.org/v2/top-headlines',
                             'country': 'ru', 'category': category}
    data = top_headlines(request_top_headlines)
    return render_template('news_main.html', data=data, title='Главная страница', form=form)


@app.route('/news_find/<q>')
def news_find(q):
    form = SearchForm()
    if form.submit():
        request_everything = {'apiKey': '162e6651da2c4734b2cfa2d940a47cc5', 'url': 'https://newsapi.org/v2/everything',
                              'q': form.search.data, 'language': 'en', 'sortBy': 'popularity'}
        data = everything(request_everything)
        return render_template('news_find.html', data=data, form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
