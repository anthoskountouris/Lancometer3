from datetime import datetime
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# DB Type information: https://docs.sqlalchemy.org/en/13/core/type_basics.html#generic-types
# Login system information: https://flask-login.readthedocs.io/en/latest/
class User(UserMixin, db.Model):
	# Internal information
	id = db.Column(db.Integer, primary_key=True)
	time_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	# Information to be provided by user
	name = db.Column(db.String(50), nullable=False)
	password = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(256), unique=True, nullable=False)
	phone = db.Column(db.String(15), unique=True, nullable=True)
	active = db.Column(db.Boolean, nullable=False, default=True)
	account_type = db.Column(db.Integer, nullable=False, default=0)

	def set_password(self, password):
		# Docs: https://werkzeug.palletsprojects.com/en/1.0.x/utils/
		self.password = generate_password_hash(password, method="pbkdf2:sha512:200000")

	def verify_password(self, password):
		return check_password_hash(self.password, password)

	def __unicode__(self):
		return self.name
