from uuid import uuid1
from flask import Blueprint, render_template, request, abort, jsonify, redirect, url_for
from flask_login import current_user, login_required
from .. import db, mongo
from datetime import datetime, timedelta
from ..decorators import internally_referred, requires_account_type
from ..models import Quiz, QuizStream
from ..user.models import User

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates", url_prefix="/a")


@admin_bp.route("/dashboard")
@login_required
@requires_account_type(3)
def dashboard():
	return render_template('admin/dashboard.html')


@admin_bp.route("/create-quiz")
@login_required
@requires_account_type(3)
def create_quiz():
	return redirect(url_for('lecturer_bp.create_quiz'))


@admin_bp.route("/manage-streams")
@login_required
@requires_account_type(3)
def manage_stream():
	# Time values for the new stream modal
	today = datetime.now()
	oneweek = today + timedelta(weeks=2)
	oneyear = today + timedelta(weeks=52)
	d1 = today.strftime("%Y-%m-%d")
	d2 = oneweek.strftime("%Y-%m-%d")
	d3 = oneyear.strftime("%Y-%m-%d")

	quizzes_to_stream = Quiz.query.filter(
		Quiz.user_id == current_user.id
	).all()

	def get_quiz_info(id):
		return Quiz.query.filter(
			Quiz.id == id
		).one()

	def get_quiz_author(id):
		return User.query.filter(
			User.id == id
		).one()

	current_streams = QuizStream.query.all()

	streams = {}
	for stream in current_streams:
		qd = get_quiz_info(stream.quiz_id)
		ud = get_quiz_author(qd.user_id)
		streams[stream.id] = {
			'quiz_author':ud.name,
			'quiz_name':qd.name,
			'quiz_type': qd.type,
			'start': stream.time_start,
			'end': stream.time_end,
			'created': stream.time_created,
			'code': stream.game_code,
			'max_players': stream.max_players
		}

	return render_template('admin/streams.html', stream_list=streams, stream_count=len(streams), quizzes_to_stream=quizzes_to_stream, tmin=d1, tmax=d2, tupper=d3)


@admin_bp.route("/manage-quiz")
@login_required
@requires_account_type(3)
def manage_quiz():
	quizzes = Quiz.query.all()

	return render_template('admin/manage.html', quiz_list=quizzes)


@admin_bp.route("/edit-quiz/<int:quiz_id>")
@login_required
def edit_quiz(quiz_id):
	return redirect(url_for('lecturer_bp.edit_quiz', quiz_id=quiz_id))


@admin_bp.route("/delete-quiz/<int:quiz_id>")
@login_required
def delete_quiz(quiz_id):
	return redirect(url_for('lecturer_bp.delete_quiz', quiz_id=quiz_id))


def check_request_args(user_args, args):
	for argument in args:
		if argument not in user_args:
			print(argument)
			return False

	return True


@admin_bp.route('/api/create-quiz', methods=['POST'])
@login_required
@internally_referred
@requires_account_type(3)
def api_create_quiz():
	if not check_request_args(request.form, ['name', 'desc', 'type']):
		return abort(400)

	user_id = current_user.id
	quiz_name = request.form.get('name')
	quiz_desc = request.form.get('desc')
	quiz_type = request.form.get('type')
	quiz_questions = request.form.getlist('questions[]')

	# Check quiz data
	quiz_uuid = str(uuid1())

	# Create quiz in SQL DB
	new_quiz = Quiz(user_id=user_id, name=quiz_name, description=quiz_desc, type=quiz_type, quiz_data_id=quiz_uuid)
	db.session.add(new_quiz)

	# Create quiz in No-SQL DB
	schema = {
		'_uuid': quiz_uuid,
		'questions': quiz_questions
	}
	print(mongo.db.quizzes)
	mongo.db.quizzes.insert_one(schema)

	db.session.commit()

	return jsonify({})


@admin_bp.route('/api/edit-quiz', methods=['GET', 'POST'])
@login_required
@internally_referred
@requires_account_type(3)
def api_edit_quiz():
	if not check_request_args(request.args, ['name', 'desc', 'type']):
		return jsonify({})

	user_id = current_user.id
	quiz_uuid = request.form.get('uuid')
	quiz_name = request.form.get('name')
	quiz_desc = request.form.get('desc')
	quiz_type = request.form.get('type')
	quiz_questions = request.form.getlist('questions[]')

	# Check quiz exists
	quiz = db.session.query(Quiz).filter(
		Quiz.quiz_data_id == quiz_uuid
	)
	if len(quiz) != 1:
		return jsonify({'error': True})

	questions = mongo.find_one({'_uuid': quiz_uuid})
	print(questions)

	# Check user is owner of quiz
	if quiz.user_id != user_id:
		return jsonify({'error': True})

	# Update data
	quiz.name = quiz_name
	quiz.description = quiz_desc
	quiz.type = quiz_type

	# Update db
	db.session.commit()

	return jsonify({'error': False})


@admin_bp.route('/api/create-stream', methods=['POST'])
@login_required
@internally_referred
@requires_account_type(3)
def api_create_stream():
	if not check_request_args(request.form, ['quiz_uuid', 'start', 'end']):
		return abort(400)

	quiz_uuid = request.form.get('quiz_uuid')
	stream_start = request.form.get('start')
	stream_end = request.form.get('end')
	max_players = request.form.get('max_players')

	# Find quiz data in db
	quiz = Quiz.quiz_data_id.filter(
		Quiz.quiz_data_id == quiz_uuid
	).one()

	if len(quiz) == 0:
		return jsonify({'error': True, 'message':'Quiz not found'})

	# Create quiz stream in SQL DB
	new_stream = QuizStream(quiz_id=quiz.id, time_start=stream_start, time_end=stream_end, max_players=max_players)
	db.session.add(new_stream)

	db.session.commit()

	return jsonify({'error': False})

