from flask import Flask,request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
from flask_babel import Babel
from datetime import timedelta
from flask_mail import Mail, Message
from sqlalchemy.dialects.mysql import base
base.MySQLCompiler.bindtemplate = "%s"


app=Flask(__name__)
# Cấu hình Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ('thieny2004py@gmail.com')
app.config['MAIL_PASSWORD'] = ('pefy ryji jsge dvmj')
app.config['MAIL_DEFAULT_SENDER'] = ('thieny2004py@gmail.com')  # Địa chỉ email gửi mặc định

mail = Mail(app)


app.config['SECRET_KEY'] = '/dffcasfwetreefawf/gchuisausahi/agsgsgs/gegweg'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/datab?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['BABEL_DEFAULT_LOCALE'] = 'en'  # Ngôn ngữ mặc định là tiếng Anh
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'vi']  # Hỗ trợ tiếng Anh và tiếng Việt
app.permanent_session_lifetime = timedelta(days=7)  # Đặt thời gian sống của session là 7 ngày
cloudinary.config(cloud_name='djikj5t0x',api_key='396263689722351',api_secret='B-kp9VtwmZ8FYbEL8LSJteg3MxU')
db=SQLAlchemy(app=app)
login=LoginManager(app=app)
login.login_view = "login-admin"

babel=Babel(app=app)

def get_locale():
  return 'vi'
babel.init_app(app, locale_selector=get_locale)
