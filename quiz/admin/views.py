from flask import url_for, request, redirect, abort
from flask_admin.contrib.sqla import ModelView as SQLAModelView
from flask_admin.contrib.pymongo import ModelView as MongoModelView
from flask_login import current_user, login_fresh
from wtforms import form, fields
from .. import flaskadmin, db, mongo
from ..user.models import User
from ..models import Quiz, QuizStream


class AdminView(SQLAModelView):
	column_exclude_list = ['password', ]

	def is_accessible(self):
		if current_user.is_authenticated:
			if current_user.get_id():
				user = User.query.get(current_user.get_id())
				if user.account_type == 4 or current_user.id == 1:
					if login_fresh():
						return True

		abort(404)

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('user_bp.login', next=request.url))


class QuizForm(form.Form):
	_uuid = fields.StringField('_uuid')
	questions = fields.StringField('questions')


class QuizView(MongoModelView):
	column_list = ('_uuid', 'questions')
	column_sortable_list = ('_uuid')
	column_searchable_list = ('_uuid')

	form = QuizForm

	def get_list(self, *args, **kwargs):
		count, data = super(QuizView, self).get_list(*args, **kwargs)

		return count, data

	def create_form(self):
		return super(QuizView, self).create_form()

	def edit_form(self, obj):
		return super(QuizView, self).edit_form(obj)


flaskadmin.add_view(AdminView(User, db.session))
flaskadmin.add_view(AdminView(Quiz, db.session, category='Quiz Data'))
flaskadmin.add_view(AdminView(QuizStream, db.session, category='Quiz Data'))
flaskadmin.add_view(QuizView(mongo.db['quizzes']))
