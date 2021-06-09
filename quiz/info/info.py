from flask import Blueprint, render_template
from quiz.play.forms import JoinGameForm

info_bp = Blueprint("info_bp", __name__, template_folder="templates", url_prefix='/lancometer')


@info_bp.route("/", methods=["GET"])
@info_bp.route("/home", methods=["GET"])
def landing_page():
	join_form = JoinGameForm(prefix='jgf')
	return render_template('landing_page.html', title="Lancometer3", join_form=join_form)


@info_bp.route("/terms")
def terms():
	return render_template('terms.html')


@info_bp.route("/privacy")
def privacy():
	return render_template('privacy.html')


@info_bp.route("/support/lecturer")
def lecturer_support():
	return render_template('lecturer_help.html')


@info_bp.route("/support/student")
def student_support():
	return render_template('student_help.html')
