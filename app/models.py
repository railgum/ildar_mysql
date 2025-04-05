from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app import login
from app import app

import click
import datetime
import os


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'User({self.username})'


class Content(db.Model):
    __tablename__ = 'content'
    id = db.Column(db.Integer, primary_key=True)
    idblock = db.Column(db.String(100), nullable=True)
    short_title = db.Column(db.String(50), nullable=True)
    img = db.Column(db.String(150), nullable=True)
    altimg = db.Column(db.String(50), nullable=True)
    title = db.Column(db.String(100), nullable=True)
    contenttext = db.Column(db.String(500), nullable=True)
    author = db.Column(db.String(100), nullable=True)
    timestampdata = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean)

    def __repr__(self):
        return f'Block({self.idblock}, {self.title})'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# Добавление пользователя
@app.cli.command('add-user')
@click.argument('name')
@click.argument('password')
def add_user(name, password):
    new_user = User(username=name, is_admin=True)
    new_user.password = new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()


# Изменение пользователя
@app.cli.command('update-user')
@click.argument('pk')
@click.argument('name')
@click.argument('password')
@click.argument('is_admin')
def update_user(pk, name, password, is_admin=True):
    user = User.query.filter_by(id=pk).one()
    if user != []:
        user.username = name
        user.password = user.set_password(password)
        user.is_admin = int(is_admin)
        db.session.commit()


# Удалить пользователя
@app.cli.command('delete-user')
@click.argument('name')
def delete_user(name):
    user = User.query.filter_by(username=name).first()
    db.session.delete(user)
    db.session.commit()


# Добавление контента
@app.cli.command('add-content')
@click.argument('idblock')
@click.argument('title')
@click.argument('contenttext')
def add_content(idblock, title, contenttext):
    date_time = datetime.datetime.now()
    new_content = Content(idblock=idblock, short_title=os.environ.get(idblock.upper()), img=None, altimg='Photo',
                          title=title, contenttext=contenttext, author=None, timestampdata=date_time, is_active=1)
    db.session.add(new_content)
    db.session.commit()


@app.cli.command('update-content')
@click.argument('pk')
@click.argument('idblock')
@click.argument('short_title')
def update_content(pk, idblock, short_title):
    content = Content.query.filter_by(id=pk).one()
    if content != []:
        content.idblock = idblock
        content.short_title = short_title
        db.session.commit()
