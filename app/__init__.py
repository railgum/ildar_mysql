from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt


import os

app = Flask(__name__)
app.config.from_object(ProductionConfig)
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bcrypt = Bcrypt(app)


from app import routes, models  # noqa
