from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES

from flask_msearch import Search
from flask_migrate import Migrate
from flask_login import LoginManager

import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SECRET_KEY']='lolol'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

bcrypt, db = Bcrypt(app), SQLAlchemy(app)
search = Search()
search.init_app(app)

migrate = Migrate(app, db)
with app.app_context():
    migrate.init_app(app, db, render_as_batch=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='userLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message = u"Kindly login to continue"


from shop.customers import routes
from shop.products import routes

from shop.carts import carts
from shop.admin import routes

