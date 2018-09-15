import os
import click
from flask.cli import with_appcontext
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
migrate = Migrate()

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY="dev",
		SQLALCHEMY_DATABASE_URI= 'sqlite:///' + os.path.join(str(app.instance_path), 'gp.sqlite',),
		SQLALCHEMY_TRACK_MODIFICATIONS= 'False',
		MAIL_SERVER = 'smtp.googlemail.com',
		MAIL_PORT = '587',
		MAIL_USE_TLS = 'True',
		MAIL_USERNAME = os.environ.get('EMAIL_USER'),
		MAIL_PASSWORD = os.environ.get('EMAIL_PASS'),

	)

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)


	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	migrate.init_app(app, db)

	from . import models

	from .users.routes import users
	from .main.routes import main
	from .errors.handlers import errors
	app.register_blueprint(users)
	app.register_blueprint(main)
	app.register_blueprint(errors)

	return app