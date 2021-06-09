from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_admin import Admin
from flask_wtf import CSRFProtect

import mimetypes

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')

db = SQLAlchemy()
mongo = PyMongo()
csrf = CSRFProtect()
flaskadmin = Admin(name='Lancometer3', template_mode='bootstrap4')
limiter = Limiter(key_func=get_remote_address, default_limits=["10000 per day", "1000 per hour"])
login_manager = LoginManager()

# Define folders
static_folder = 'static'
template_folder = 'templates'


def create_app():
	app = Flask(__name__, template_folder=template_folder, instance_relative_config=False, static_folder=static_folder)
	app.config.from_object('config.Config')

	db.init_app(app)
	mongo.init_app(app)
	login_manager.init_app(app)
	limiter.init_app(app)
	csrf.init_app(app)
	flaskadmin.init_app(app)

	with app.app_context():
		from . import routes
		from .admin import admin, views
		from .errors import error
		from .info import info
		from .lecturer import lecturer
		from .play import play
		from .student import student
		from .user import user
		from .upload import upload

		app.register_blueprint(routes.main)
		app.register_blueprint(admin.admin_bp)
		app.register_blueprint(error.error_bp)
		app.register_blueprint(info.info_bp)
		app.register_blueprint(lecturer.lecturer_bp)
		app.register_blueprint(play.play_bp)
		app.register_blueprint(student.student_bp)
		app.register_blueprint(user.user_bp)
		app.register_blueprint(upload.upload_bp)

		db.create_all()
		login_manager.login_view = "user_bp.login"
		login_manager.refresh_view = "user_bp.reauth"
		login_manager.needs_refresh_message = (
			u"To protect your account, please reauthenticate to access this page."
		)
		login_manager.needs_refresh_message_category = "warning"

		@app.after_request
		def apply_headers(response):
			response.headers['Server'] = 'Lancometer3'
			response.headers['Cross-Origin-Resource-Policy'] = 'same-site'

			if not request.path.startswith('/static/') and not request.path.startswith('/api/'):
				response.headers["Permissions-Policy"] = "accelerometer=(), geolocation=(self), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), interest-cohort=()"
				response.headers['Referrer-Policy'] = "no-referrer-when-downgrade"
				response.headers['X-Frame-Options'] = "Deny"
				response.headers['X-XSS-Protection'] = "1; mode=block"
				response.headers['X-Content-Type-Options'] = "nosniff"

			return response

		return app


app = create_app()
