from os import environ
from dotenv import load_dotenv

load_dotenv()


class Config:

	TESTING = environ.get('TESTING')
	DEBUG = environ.get('FLASK_DEBUG')
	SECRET_KEY = environ.get('SECRET_KEY')

	SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')
	# SESSION_COOKIE_SECURE = environ.get('SESSION_COOKIE_SECURE')
	SESSION_TYPE = environ.get('SESSION_TYPE')
	SESSION_TABLE = environ.get('SESSION_TABLE')

	UPLOADED_FILES_DEST = environ.get('UPLOADED_FILES_DEST')

	SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
	MONGO_URI = environ.get('MONGO_URI')

	SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
	SQLALCHEMY_POOL_RECYCLE = 90
