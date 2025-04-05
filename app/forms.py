from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


# class ContentForm(FlaskForm):
#     short_title = StringField('short_title', validators=[DataRequired()])
#     img = StringField('img', validators=[DataRequired()])
#     altimg = StringField('altimg', validators=[DataRequired()])
#     title = StringField('title', validators=[DataRequired()])
#     contenttext = StringField('contenttext', validators=[DataRequired()])
