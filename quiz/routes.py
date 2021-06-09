from flask import Blueprint, redirect, url_for, session, send_from_directory, request
from . import static_folder
from flask_login import current_user

main = Blueprint("main", __name__)


@main.route('/robots.txt')
@main.route('/security.txt')
def static_from_root():
	return send_from_directory(static_folder, request.path[1:])

@main.route("/")
def index():
	if session.get('game_code') is not None:
		return redirect(url_for('play_bp.game'))

	if current_user.is_authenticated:
		# Check account type
		# Check if game session is active
		return redirect(url_for('play_bp.enter_code'))
	else:
		return redirect(url_for('info_bp.landing_page'))
