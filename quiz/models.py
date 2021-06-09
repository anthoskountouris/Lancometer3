from datetime import datetime
from sqlalchemy import Integer, Sequence, UniqueConstraint
from sqlalchemy_utils import UUIDType
from quiz import db


class Quiz(db.Model):
	__tablename__ = 'quizzes'

	id = db.Column(Integer, Sequence('quiz_id_seq'), primary_key=True)
	user_id = db.Column(Integer, db.ForeignKey('user.id'))
	quiz_data_id = db.Column(UUIDType(binary=False), nullable=False)

	time_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	name = db.Column(db.String(50), nullable=False)
	type = db.Column(db.String(50), nullable=False)
	description = db.Column(db.Text, nullable=False, default='No description')

	def __repr__(self):
		return "<Quiz(id='%s', user='%s', name='%s')>" % (self.id, self.user_id, self.name)


class QuizStream(db.Model):
	__tablename__ = 'streams'

	id = db.Column(Integer, Sequence('quiz_id_seq'), primary_key=True)
	user_id = db.Column(Integer, db.ForeignKey('user.id'))
	quiz_id = db.Column(Integer, db.ForeignKey('quizzes.id'))
	time_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	time_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	time_end = db.Column(db.DateTime, nullable=False)

	max_players = db.Column(db.Integer, nullable=False, default=512)
	game_code = db.Column(db.Text, nullable=False)

	def __repr__(self):
		return "<QuizStream(id='%s', quiz='%s', start='%s')>" % (self.id, self.quiz_id, self.time_start)
