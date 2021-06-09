from time import time
from uuid import uuid1
import sqlalchemy.orm.exc, json, base64
from random import choice as rc, randint
from flask import (
	Blueprint,
	render_template,
	request,
	abort,
	jsonify,
	flash,
	redirect,
	url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import desc
from .forms import DeleteForm
from .. import db, mongo, csrf
from datetime import datetime, timedelta
from ..decorators import internally_referred, requires_account_type
from ..models import Quiz, QuizStream

lecturer_bp = Blueprint(
	"lecturer_bp", __name__, template_folder="templates", url_prefix="/l"
)


def get_streams_for_quiz(quiz_id):
	return QuizStream.query.filter(QuizStream.quiz_id == quiz_id).all()


@lecturer_bp.route("/dashboard")
@login_required
@requires_account_type(2)
def dashboard():
	# Get recent quizzes from database
	quiz_list = (
		Quiz.query.filter(Quiz.user_id == current_user.id)
			.order_by(desc(Quiz.time_created))
			.limit(6)
			.all()
	)

	if len(quiz_list) == 0:
		quiz_list = []

	quizzes = []

	for quiz in quiz_list:
		streams = get_streams_for_quiz(quiz.id)
		max_participants = 1
		stream_length = []
		end_string = ""

		if len(streams) != 0:
			for stream in streams:
				max_participants += stream.max_players
				stream_length.append(stream.time_end)

			if max(stream_length) > datetime.now():
				end_date = max(stream_length) - datetime.now()
				if end_date > timedelta(days=1):
					end_string = '' #f"{end_date.days} day(s)"
				else:
					end_string = '' #f"{end_date.hours} hour(s)"

		responses = randint(1, max_participants)
		quizzes.append({
			"id": quiz.id,
			"name": quiz.name,
			"desc": quiz.description,
			"streams": len(streams),
			"max_participants": max_participants,
			'players_completed': responses,
			'players_percent': round(responses / max_participants * 100, 2),
			"end_string": end_string
		})
	print(quiz_list)

	return render_template("lecturer/dashboard.html", recent_quizzes=quizzes)


@lecturer_bp.route("/create-quiz")
@login_required
@requires_account_type(2)
def create_quiz():
	return render_template("lecturer/create.html")


@lecturer_bp.route("/manage-streams")
@login_required
@requires_account_type(2)
def manage_stream():
	# Time values for the new stream modal
	today = datetime.now()
	oneweek = today + timedelta(weeks=2)
	oneyear = today + timedelta(weeks=52)
	d1 = today.strftime("%Y-%m-%d")
	d2 = oneweek.strftime("%Y-%m-%d")
	d3 = oneyear.strftime("%Y-%m-%d")

	quizzes_to_stream = Quiz.query.filter(Quiz.user_id == current_user.id).all()

	def get_quiz_info(id):
		return Quiz.query.filter(Quiz.id == id).one()

	current_streams = QuizStream.query.filter(
		QuizStream.user_id == current_user.id
	).all()

	streams = {}
	for stream in current_streams:
		qd = get_quiz_info(stream.quiz_id)
		streams[stream.id] = {
			"quiz_name": qd.name,
			"quiz_type": qd.type,
			"start": stream.time_start,
			"end": stream.time_end,
			"has_started": datetime.timestamp(stream.time_start) < time(),
			"has_ended": datetime.timestamp(stream.time_end) < time(),
			"created": stream.time_created,
			"code": stream.game_code,
			"max_players": stream.max_players
		}

	return render_template(
		"lecturer/streams.html",
		stream_list=streams,
		stream_count=len(streams),
		quizzes_to_stream=quizzes_to_stream,
		tmin=d1,
		tmax=d2,
		tupper=d3,
	)


@lecturer_bp.route("/manage-quiz")
@login_required
@requires_account_type(2)
def manage_quiz():
	quizzes = Quiz.query.filter(Quiz.user_id == current_user.id).all()

	quiz_list = []
	for quiz in quizzes:
		quiz_list.append(
			{
				"id": quiz.id,
				"name": quiz.name,
				"time_created": quiz.time_created,
				"streams": len(get_streams_for_quiz(quiz.id)),
			}
		)

	return render_template("lecturer/manage.html", quiz_list=quiz_list)


@lecturer_bp.route("/edit-quiz/<int:quiz_id>")
@login_required
@requires_account_type(2)
def edit_quiz(quiz_id):
	try:
		quiz = Quiz.query.filter(
			Quiz.id == quiz_id, Quiz.user_id == current_user.id
		).one()
	except sqlalchemy.orm.exc.NoResultFound:
		return abort(404)

	mongo_data = mongo.db.quizzes.find_one_or_404({"_uuid": str(quiz.quiz_data_id)})
	print(mongo_data)

	return render_template(
		"lecturer/edit.html", quiz_data=quiz, question_data=mongo_data, quiz_id=quiz_id
	)


@lecturer_bp.route("/delete-quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
@requires_account_type(2)
def delete_quiz(quiz_id):
	dqf = DeleteForm()

	if dqf.validate_on_submit():
		# Get quiz data
		qtd = Quiz.query.filter(
			Quiz.id == quiz_id, Quiz.user_id == current_user.id
		).one()
		qsl = QuizStream.query.filter(QuizStream.quiz_id == quiz_id).all()

		print(qtd)
		if Quiz is None:
			flash("Could not find that quiz", "danger")
		else:
			# Delete all quiz streams for that quiz
			for qs in qsl:
				print(qs)
				db.session.delete(qs)

			# Remove that specific quiz
			db.session.delete(qtd)

			# TODO: Remove data from mongodb

			# Commit deletion if mongo deletion succeeds
			db.session.commit()
			flash("Quiz deleted successfully", "info")

		return redirect(url_for("lecturer_bp.manage_quiz"))

	return render_template("lecturer/delete.html", delete_form=dqf, mode="Quiz")


@lecturer_bp.route("/delete-stream/<int:stream_id>", methods=["GET", "POST"])
@login_required
@requires_account_type(2)
def delete_stream(stream_id):
	dqf = DeleteForm()

	if dqf.validate_on_submit():
		# Get quiz data
		qsd = QuizStream.query.filter(QuizStream.id == stream_id, Quiz.user_id == current_user.id).one()

		if QuizStream is None:
			flash("Could not find that stream", "danger")
		else:
			# Remove that specific quiz
			db.session.delete(qsd)

			# TODO: Remove data from mongodb

			# Commit deletion if mongo deletion succeeds
			db.session.commit()
			flash("Stream deleted successfully", "info")

		return redirect(url_for("lecturer_bp.manage_stream"))

	return render_template("lecturer/delete.html", delete_form=dqf, mode="Stream")


def check_request_args(user_args, args):
	for argument in args:
		if argument not in user_args:
			print(argument)
			return False

	return True


@lecturer_bp.route("/api/create-quiz", methods=["POST"])
@login_required
@internally_referred
@requires_account_type(3)
@csrf.exempt
def api_create_quiz():
	if not check_request_args(request.form, ["name", "desc", "type"]):
		return abort(400)

	user_id = current_user.id
	quiz_schema = request.form
	quiz_name = quiz_schema["name"]
	quiz_desc = quiz_schema["desc"]
	quiz_type = quiz_schema["type"]
	quiz_questions = json.loads(base64.b64decode(quiz_schema["questions"]))
	print(quiz_questions)

	# Check quiz data
	quiz_uuid = str(uuid1())

	# Create quiz in SQL DB
	new_quiz = Quiz(
		user_id=user_id,
		name=quiz_name,
		description=quiz_desc,
		type=quiz_type,
		quiz_data_id=quiz_uuid,
	)
	db.session.add(new_quiz)

	# Create quiz in No-SQL DB
	schema = {"_uuid": quiz_uuid, "questions": quiz_questions}
	print(mongo.db.quizzes)
	mongo.db.quizzes.insert_one(schema)

	db.session.commit()

	return jsonify({"error": False, "quiz_uuid": quiz_uuid, "id": new_quiz.id})


@lecturer_bp.route("/api/edit-quiz", methods=["GET", "POST"])
@login_required
@internally_referred
@requires_account_type(3)
def api_edit_quiz():
	if not check_request_args(request.form, ["uuid", "name", "desc", "type"]):
		return jsonify({})

	user_id = current_user.id
	quiz_uuid = request.form.get("uuid")
	quiz_name = request.form.get("name")
	quiz_desc = request.form.get("desc")
	quiz_type = request.form.get("type")

	# Check quiz exists
	quiz = Quiz.query.filter_by(quiz_data_id=quiz_uuid).one()

	# questions = mongo.db.quizzes.find_one({'_uuid': quiz_uuid})

	# Check user is owner of quiz
	if quiz.user_id != user_id:
		return jsonify({"error": True})

	# Update data
	quiz.name = quiz_name
	quiz.description = quiz_desc
	quiz.type = quiz_type

	# Update db
	db.session.commit()

	flash("Updated quiz!", "success")

	return jsonify({"error": False})


@lecturer_bp.route("/api/stream-quiz", methods=["POST"])
@login_required
@internally_referred
@requires_account_type(3)
def api_create_stream():
	if not check_request_args(request.form, ["quiz_uuid", "start", "end"]):
		return abort(400)

	quiz_uuid = request.form.get("quiz_uuid")
	stream_start = request.form.get("start")
	stream_end = request.form.get("end")
	max_players = request.form.get("max_players")

	# Find quiz data in db
	try:
		quiz = Quiz.query.filter(
			Quiz.user_id == current_user.id, Quiz.quiz_data_id == quiz_uuid
		).one()
	except sqlalchemy.orm.exc.NoResultFound:
		return jsonify({"error": True, "message": "Quiz not found"})

	def make_game_code():
		words = ["game", "learn", "fun", "dog", "cat", "milk", "cheese", "laptop"]
		return rc(words) + "-" + rc(words) + "-" + rc(words)

	game_code = make_game_code()

	# Create quiz stream in SQL DB
	new_stream = QuizStream(
		user_id=current_user.id,
		quiz_id=quiz.id,
		time_start=stream_start,
		time_end=stream_end,
		max_players=max_players,
		game_code=game_code,
	)
	db.session.add(new_stream)
	db.session.commit()

	return jsonify({"error": False, "code": game_code})
