from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads
from flask_msearch import Search
from flask_login import LoginManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
DB_NAME = "myshop.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SECRET_KEY'] = 'MYSISTERSARETHEBEST'
app.config["UPLOADED_PHOTOS_DEST"] = "shop/static/img"
db.init_app(app)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app)

migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='customerLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message = u'Please login first'

basedir = os.path.abspath(os.path.dirname(__file__))
photos = UploadSet("photos", IMAGES)
configure_uploads(app, photos)

from .admin import routes
from shop.products import routes
from shop.carts import carts
from shop.customers import routes   

def create_database(app):
    if not path.exists('travel/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')