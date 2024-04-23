import datetime
import json

import requests
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required

from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm, SearchForm, GeoForm

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
    req = requests.get(f'{params["url"]}?'
                       f'apiKey={params["apiKey"]}&'
                       f'q={params["q"]}&'
                       f'language={params["language"]}&'
                       f'sortBy={params["sortBy"]}')
    json_req = req.json()
    return json_req


# новости для главной страницы по категории
def top_headlines(params):
    req = requests.get(f'{params["url"]}?'
                       f'apiKey={params["apiKey"]}&'
                       f'country={params["country"]}&'
                       f'category={params["category"]}')
    json_req = req.json()
    return json_req


def toponym_by_geocode(geocode):
    yandex_req = requests.get(
        f'http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={geocode}&lang=en_US'
        f'&format=json')
    yandex_json = yandex_req.json()

    toponym = yandex_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]
    toponym_coodrinates = toponym["Point"]["pos"]

    return {'address': toponym_address, 'cords': toponym_coodrinates.replace(' ', ',')}


def urlImage_by_ll(ll, toponym):
    yandex_req = requests.get(
        f'http://static-maps.yandex.ru/1.x/?ll={ll}&spn=10,1&size=600,300&l=map&pt={toponym["cords"]},flag')

    return yandex_req.url


def weather_by_ll(ll):
    lat = ll.split(',')[0]
    lon = ll.split(',')[1]
    url_yandex = f'https://api.weather.yandex.ru/v2/informers/?lat={lat}&lon={lon}&[lang=ru_RU]'
    yandex_req = requests.get(url_yandex, headers={'X-Yandex-API-Key': '31edec50-cbef-4e12-a56f-8414eb65f234'},
                              verify=False)
    yandex_json = json.loads(yandex_req.text)
    return {'image': f"https://yastatic.net/weather/i/icons/funky/dark/{yandex_json['fact']['icon']}.svg",
            'temp': yandex_json["fact"]['temp'], 'feels_like': yandex_json['fact']['feels_like']}


@app.route('/', methods=['GET', 'POST'])
@app.route('/news_main', methods=['GET', 'POST'])
def news_main():
    geoform = GeoForm()
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(f'/news_find/{form.search.data}')
    request_top_headlines = {'apiKey': '162e6651da2c4734b2cfa2d940a47cc5',
                             'url': 'https://newsapi.org/v2/top-headlines',
                             'country': 'us', 'category': 'general'}
    data = top_headlines(request_top_headlines)
    return render_template('news_main.html', data=data, title='Главная страница', form=form)


@app.route('/news_main/<category>', methods=['GET', 'POST'])
def news_main_category(category):
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(f'/news_find/{form.search.data}')
    request_top_headlines = {'apiKey': '162e6651da2c4734b2cfa2d940a47cc5',
                             'url': 'https://newsapi.org/v2/top-headlines',
                             'country': 'us', 'category': category}
    data = top_headlines(request_top_headlines)
    return render_template('news_main.html', data=data, title='Главная страница', form=form)


@app.route('/news_find/<q>', methods=['GET', 'POST'])
def news_find(q):
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(f'/news_find/{form.search.data}')
    request_everything = {'apiKey': '162e6651da2c4734b2cfa2d940a47cc5', 'url': 'https://newsapi.org/v2/everything',
                          'q': q, 'language': 'en', 'sortBy': 'popularity'}
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
    '''scaascx'''
