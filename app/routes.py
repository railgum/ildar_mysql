import sqlalchemy as sa
import datetime
import os
from flask import render_template, redirect, url_for, request
from app import app, db
from app.forms import LoginForm
from app.models import User, Content
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from app import csrf
import functions as fun
import git


@app.route('/')
@app.route('/index')
def index():
    # получить все записи из БД
    q = db.session.query(Content).all()
    json_data = {}

    # Группировка данных в словарь JSON (jsonify?)
    for raw in q:
        # Создание новой записи, если ключ еще не существует
        if raw.idblock not in json_data:
            json_data[raw.idblock] = []
        # Добавление данных в существующий ключ
        if raw.is_active == 0:
            continue
        else:
            json_data[raw.idblock].append({
                'id': raw.id,
                'short_title': raw.short_title,
                'img': raw.img,
                'altimg': raw.altimg,
                'title': raw.title,
                'contenttext': raw.contenttext,
                'author': raw.author,
                'timestampdata': raw.timestampdata,
                'is_active': raw.is_active
            })

        context = {
            'SLIDER': os.environ.get('SLIDER_ID'),
            'MINICARD': os.environ.get('MINICARD_ID'),
            'FEATURETTE': os.environ.get('FEATURETTE_ID'),
            'FOOTER': os.environ.get('FOOTER_ID'),
            'json_data': json_data,
        }
    return render_template('landing.html', **context)


# Вход в админ-панель
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_panel'))
    form = LoginForm()
    error = None

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(
            User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            error = 'Неверное имя пользователя или пароль'
            return render_template('login_adm.html', title='Войти', form=form, error=error)
        elif not user.is_admin:
            error = 'Пользователь заблокирован'
            return render_template('login_adm.html', title='Войти', form=form, error=error)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('admin_panel')
        return redirect(next_page)
    return render_template('login_adm.html', title='Войти', form=form, error=error)


# Выход из админки
@app.route('/logout')
def logout():
    logout_user()
    # перенаправление на главную страницу или страницу входа
    return redirect(url_for('index'))


# Страница админ панели
@app.route('/admin_panel')
@login_required
def admin_panel():
    blocks = Content.query.all()
    ERROR_COUNT_SLIDER = (Content.query.filter(
        Content.idblock == os.environ.get('SLIDER_ID')).count()) > int(os.environ.get('MAX_COUNT_SLIDER'))
    ERROR_COUNT_MINICARD = (Content.query.filter(
        Content.idblock == os.environ.get('MINICARD_ID')).count()) > int(os.environ.get('MAX_COUNT_MINICARD'))
    ERROR_COUNT_FEATURETTE = (Content.query.filter(
        Content.idblock == os.environ.get('FEATURETTE_ID')).count()) > int(os.environ.get('MAX_COUNT_FEATURETTE'))
    # Группировка данных в словарь JSON
    json_data = {}
    for raw in blocks:
        # Создание новой записи, если ключ еще не существует
        if raw.idblock not in json_data:
            json_data[raw.idblock] = []

        json_data[raw.idblock].append({
            'id': raw.id,
            'short_title': raw.short_title,
            'img': raw.img,
            'altimg': raw.altimg,
            'title': raw.title,
            'contenttext': raw.contenttext,
            'author': raw.author,
            'timestampdata': raw.timestampdata,
            'is_active': raw.is_active
        })
    context = {
        'json_data': json_data,
        'SLIDER': os.environ.get('SLIDER_ID'),
        'MINICARD': os.environ.get('MINICARD_ID'),
        'FEATURETTE': os.environ.get('FEATURETTE_ID'),
        'FOOTER': os.environ.get('FOOTER_ID'),
        'ERROR_COUNT_SLIDER': ERROR_COUNT_SLIDER,
        'ERROR_COUNT_MINICARD': ERROR_COUNT_MINICARD,
        'ERROR_COUNT_FEATURETTE': ERROR_COUNT_FEATURETTE,
    }
    # передаем json на фронт - далее нужно смотреть admin_panel.html и обрабатывать там
    return render_template('admin_panel.html', **context)


# Обновление информации
@app.route('/update_content', methods=['POST'])
@login_required
@csrf.exempt
def update_content():
    short_title = request.form['short_title']
    altimg = 'Photo'
    author = request.form['author']
    date_time = datetime.datetime.now()
    idblock = request.form['id_block']
    title = request.form['title']
    contenttext = request.form['contenttext']

    if 'new_item' in request.form:
        new_title = request.form['new_title']
        new_contenttext = request.form['new_contenttext']
        new_img_file = request.files['new_img']
        imgpath = fun.process_img_file(new_img_file, short_title)
        new_item = Content(idblock=idblock, short_title=short_title, img=imgpath, altimg=altimg, title=new_title,
                           contenttext=new_contenttext, author=author, timestampdata=date_time, is_active=True)
        db.session.add(new_item)
        db.session.commit()
    elif 'deactivate' in request.form:
        content_id = request.form['id']
        deact_cont = Content.query.filter_by(id=content_id).first()
        deact_cont.is_active = False
        db.session.commit()
    elif 'activate' in request.form:
        content_id = request.form['id']
        act_cont = Content.query.filter_by(id=content_id).first()
        act_cont.is_active = True
        db.session.commit()
    else:
        content_id = request.form['id']
        file = request.files['img']
        imgpath = fun.process_img_file(file, short_title)
        new_cont = Content.query.filter_by(id=content_id).first()
        new_cont.title = title
        new_cont.author = author
        new_cont.contenttext = contenttext
        new_cont.timestampdata = date_time
        if file:
            new_cont.img = imgpath
        db.session.commit()

    return redirect(url_for('admin_panel'))


# Вебхук
@app.route('/update_server', methods=['POST'])
@csrf.exempt
def webhook():
    if request.method == 'POST':
        repo = git.Repo('https://github.com/railgum/ildar_mysql.git')
        origin = repo.remotes.origin

        origin.pull()

        return 'Updated PythonAnyWhere successfully!', 200
    else:
        return 'Wrong event type', 400
