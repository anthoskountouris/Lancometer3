import random

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, abort
from flask_login import current_user
from .. import db, mongo, limiter
from ..models import QuizStream, Quiz
from .forms import JoinGameForm
from datetime import datetime
from time import time

from ..user.models import User

play_bp = Blueprint("play_bp", __name__, template_folder="templates")


@limiter.request_filter
def user_whitelist():
	if not current_user.is_authenticated:
		return False

	# Don't rate limit user accounts greater than type 2
	return current_user.account_type > 2


def resp(data=None, **kwargs):
	err = False
	msg = ''
	if 'error' in kwargs:
		err = True
		msg = kwargs['error']

	return jsonify({
		'license': 'This API data is private and only available for use with permission',
		'error': err,
		'message': msg,
		'response': data
	})


@limiter.limit('300/day;100/hour;1/minute', override_defaults=True)
@play_bp.route('/api/game/load', methods=['GET'])
def load_game_data():
	if session.get('game_code') is None:
		return resp({}, error='You are not in a game.')

	game_data = {}

	qsd = db.session.query(QuizStream).filter(
		QuizStream.game_code == session['game_code']
	).one()
	qgd = db.session.query(Quiz).filter(
		Quiz.id == qsd.quiz_id
	).one()
	quiz_uuid = str(qgd.quiz_data_id)

	mongo_data = mongo.db.quizzes.find_one({'_uuid': quiz_uuid})

	game_data['name'] = qgd.name
	game_data['desc'] = qgd.description
	game_data['start'] = qsd.time_start
	game_data['end'] = qsd.time_end
	game_data['start_ts'] = datetime.timestamp(qsd.time_start)
	game_data['end_ts'] = datetime.timestamp(qsd.time_end)
	game_data['questions'] = dict(mongo_data['questions'])

	return resp(game_data)


@limiter.limit('300/day;100/hour;10/minute', override_defaults=True)
@play_bp.route('/api/game/answer', methods=['POST'])
def save_game_data():
	if session.get('game_code') is None:
		return resp({}, error='You are not in a game.')

	return resp({})


@limiter.limit('30/day;15/hour;5/minute', override_defaults=True)
@play_bp.route('/entry', methods=['GET', 'POST'])
def enter_code():
	join_form = JoinGameForm(prefix='jgf')

	if session.get('game_code') is not None:
		flash('You are already in a game, you must leave before joining a new one', 'danger')
		return redirect(url_for('play_bp.game'))

	if request.method == 'POST' and join_form.validate_on_submit():
		user_game_code = join_form.game_code.data

		# Check code exists in database
		code_results = db.session.query(QuizStream).filter(
			QuizStream.game_code == user_game_code
		).all()

		can_play = False
		# If code exists, set it in session variable
		if len(code_results) == 1:
			qsd = code_results[0]
			# TODO: Check we can play game (within player total count)
			can_play = True

			# Check if quiz has started / ended
			start_ts = datetime.timestamp(qsd.time_start)
			end_ts = datetime.timestamp(qsd.time_end)

			if start_ts > time():
				flash('This game has not started yet. Start date: ' + str(qsd.time_start), 'warning')
				can_play = False

			if end_ts < time():
				flash('This game has finished! Game ended: ' + str(qsd.time_end), 'danger')
				can_play = False
		else:
			flash('This game code is invalid', 'danger')

		if can_play:
			session['game_code'] = user_game_code
			return redirect(url_for('play_bp.game'))

	return render_template('play/enter.html', join_form=join_form)


@play_bp.route('/join/<quiz_stream_id>')
def join_game(quiz_stream_id):
	if quiz_stream_id is None:
		return abort(400)

	# Check code exists in database
	code_results = db.session.query(QuizStream).filter(
		QuizStream.id == quiz_stream_id
	).one()

	# If code exists, set it in session variable
	if code_results:
		print(code_results)
		flash('Welcome to Lancometer 3.0!')
		session['game_code'] = code_results.game_code
		return redirect(url_for('play_bp.game'))
	else:
		return abort(400)


@play_bp.route('/leave', methods=['GET'])
def leave_game():
	session.pop('game_code', None)
	flash('You have left the game', 'info')
	return redirect(url_for('play_bp.enter_code'))


@limiter.limit('200/day;50/hour;10/minute', override_defaults=True)
@play_bp.route('/game', methods=['GET'])
def game():
	return render_template('play/game.html')


@play_bp.route('/game/settings', methods=['GET'])
def game_settings():
	return render_template('play/settings.html')


@play_bp.route('/game/leaderboard', methods=['GET'])
def game_leaderboard():
	user_list = db.session.query(User).all()

	players = []
	for user in user_list:
		players.append({
			'name': user.name,
			'score': random.randint(0, 5)
		})


	return render_template('play/leaderboard.html', player_list=players)

