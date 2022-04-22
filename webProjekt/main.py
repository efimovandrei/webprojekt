from flask import Flask, render_template, url_for, redirect, abort, request
from data import db_session
from data.users import User
from data.news import News
from data.obs import Obs
from data.sob import Sob
from forms.user import RegisterForm, LoginForm
from forms.news import NewsForm
from forms.obs_form import ObsForm
from forms.sobs import SobForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key_webprojekt'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            db_sess.commit()
            return redirect('/news')
        else:
            abort(404)
    return render_template('news_red.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


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


@app.route("/news")
def index():
    db_session.global_init("db/blogs.db")
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    teacher = db_sess.query(User).filter(User.id == current_user.id)
    return render_template("news.html", news=news, teacher=teacher)


@app.route("/user")
def users():
    db_session.global_init("db/blogs.db")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id)
    return render_template("user.html", user=user)


@app.route("/sob")
def indexsob():
    db_session.global_init("db/blogs.db")
    db_sess = db_session.create_session()
    sob = db_sess.query(Sob)
    teacher = db_sess.query(User).filter(User.id == current_user.id)
    return render_template("sob.html", sob=sob, teacher=teacher)


@app.route("/obs/<int:id>", methods=['GET', 'POST'])
def obs(id):
    db_session.global_init("db/blogs.db")
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      ).first()
    obs = db_sess.query(Obs).filter(Obs.news_id == id,
                                    )
    return render_template("obs.html", news=news, title=news.title, id=news.id, obs=obs)


@app.route('/obs_add/<int:id>', methods=['GET', 'POST'])
@login_required
def obs_news(id):
    form = ObsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        obs = Obs()
        obs.content = form.content.data
        obs.name = form.name.data
        news = db_sess.query(News).filter(News.id == id,
                                          ).first()
        obs.news_id = news.id
        db_sess.add(obs)
        db_sess.commit()
        return redirect(f'/obs/{id}')
    return render_template('obs_red.html', title='Добавление комментария',
                           form=form)


@app.route('/news_add', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/news')
    return render_template('news_red.html', title='Добавление новости',
                           form=form)


@app.route('/sob_add', methods=['GET', 'POST'])
@login_required
def add_sob():
    form = SobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        sob = Sob()
        sob.title = form.title.data
        sob.content = form.content.data
        sob.date = form.date.data
        db_sess.add(sob)
        db_sess.commit()
        return redirect('/sob')
    return render_template('sob_red.html', title='Добавление новости',
                           form=form)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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
            about=form.about.data,
            is_teacher=form.is_teacher.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run()
