from flask import (
	Blueprint,
	render_template,
	redirect,
	url_for,
	flash,
	request,
	Response,
)
from flask_login import (
	login_user,
	current_user,
	logout_user,
	login_required,
	login_fresh,
	confirm_login,
)
from .forms import (
	UpdatePasswordForm,
	UpdateEmailForm,
	DeleteAccountForm,
	LoginForm,
	SignupForm,
	ReAuthUserForm,
	DownloadAccountForm,
)
from .models import db, User
from .. import login_manager
from time import time

from ..models import Quiz, QuizStream

user_bp = Blueprint("user_bp", __name__, template_folder="templates")


@user_bp.route("/clear-cache", methods=["GET"])
def clear_cache():
	flash("Action successful. Your browser was told to clear its cache.", "success")

	resp = redirect(url_for("user_bp.account"))
	resp.headers["Clear-Site-Data"] = '"cache"'

	return resp


@user_bp.route("/clear-all", methods=["GET"])
def clear_all():
	flash("Your browser has been told to remove all Lancometer data", "info")

	resp = redirect(url_for("user_bp.login"))
	resp.headers["Clear-Site-Data"] = '"*"'

	return resp


@user_bp.route("/logout")
@login_required
def logout():
	"""User log-out logic."""
	logout_user()
	return redirect(url_for("main.index"))


@user_bp.route("/login", methods=["GET", "POST"])
def login():
	# Bypass if user is logged in
	if current_user.is_authenticated:
		return redirect(request.args.get("next") or url_for("user_bp.account"))

	login_form = LoginForm()
	if login_form.validate_on_submit():
		email = login_form.email.data
		password = login_form.password.data
		user = User.query.filter_by(email=email).first()

		if user and user.verify_password(password=password):
			login_user(user)
			return redirect(request.args.get("next") or url_for("main.index"))

		flash("Doesn't seem quite right. Try again?", "danger")

	return render_template("login.html", form=login_form, title="login")


@user_bp.route("/reauth", methods=["GET", "POST"])
def reauth():
	reauth_form = ReAuthUserForm(prefix="reauth")

	if login_fresh():
		flash("You do not need to re-authenticate", "warning")
		return redirect(url_for("user_bp.account"))

	if request.method == "POST" and reauth_form.validate_on_submit():
		user = User.query.filter_by(id=current_user.id).first()

		if user is None:
			flash("Could not log you in, please try again.", "danger")
		elif not user.verify_password(reauth_form.password.data):
			flash("Password was not correct", "danger")
		elif user.active == 0:
			flash("Your account is not active", "danger")
		else:
			confirm_login()
			flash("You have been re-authenticated", "success")
			next_url = request.args.get("next")
			return redirect(next_url or url_for("user_bp.account"))

	return render_template(
		"reauth.html", title="Re-authenticate Please", reauth_form=reauth_form
	)


@user_bp.route("/signup", methods=["GET", "POST"])
def signup():
	# Bypass if user is logged in
	if current_user.is_authenticated:
		return redirect(request.args.get("next") or url_for("user_bp.account"))

	signup_form = SignupForm()
	if signup_form.validate_on_submit():
		name = signup_form.name.data
		email = signup_form.email.data
		phone = signup_form.phone.data
		password = signup_form.password.data

		passed_validation = True

		# Check phone against database
		if User.query.filter_by(phone=phone).first() is not None:
			flash("Phone number already in use. Try logging in?", "warning")
			passed_validation = False

		# Check email against database
		if User.query.filter_by(email=email).first() is not None:
			flash("Email already in use. Try logging in?", "warning")
			passed_validation = False

		# If checks passed we can create account and redirect user
		if passed_validation:
			user = User(name=name, email=email, phone=phone)
			user.set_password(password)
			db.session.add(user)
			db.session.commit()

			# Log in as newly created user
			login_user(user)
			return redirect(url_for("main.index"))

	return render_template("signup.html", title="sign up", form=signup_form)


@login_manager.user_loader
def load_user(user_id):
	if user_id is not None:
		return User.query.get(user_id)
	return None


@user_bp.route("/account")
@login_required
def account():
	return render_template("account.html")


@user_bp.route("/email", methods=["GET", "POST"])
@login_required
def email():
	email_form = UpdateEmailForm()

	if request.method == "POST" and email_form.validate_on_submit():
		entered_email = email_form.new_email.data
		entered_pass = email_form.password.data
		update_user = User.query.filter_by(id=current_user.id).first()

		# Check password is correct
		if not current_user.verify_password(entered_pass):
			flash("Account password was incorrect.", "danger")
			return redirect(url_for("user_bp.account"))

		# If user has re-entered password we can mark their session as fresh
		confirm_login()

		# Check if email already in use
		results = User.query.filter_by(email=entered_email).all()
		if len(results) > 0:
			flash("This email is already in use", "warning")
			return redirect(url_for("user_bp.account"))

		update_user.email = entered_email
		db.session.commit()

		flash("Email was updated!", "success")
		return redirect(url_for("user_bp.account"))

	return render_template("email.html", change_email=email_form)


@user_bp.route("/password", methods=["GET", "POST"])
@login_required
def password():
	password_form = UpdatePasswordForm()
	update_user = User.query.filter_by(id=current_user.id).first()

	if request.method == "POST" and password_form.validate_on_submit():
		entered_pass = password_form.old_password.data
		entered_newpass = password_form.new_password.data

		# Check password is correct
		if not current_user.verify_password(entered_pass):
			flash("Current password was incorrect.", "danger")
		else:
			# If user has re-entered password we can mark their session as fresh
			confirm_login()

			# Update user password
			update_user.password = entered_newpass
			db.session.commit()

			# Let user know about success and redirect
			flash("Password was updated!", "success")
			return redirect(url_for("user_bp.account"))

	return render_template("password.html", change_password=password_form)


@user_bp.route("/download", methods=["GET", "POST"])
@login_required
def download():
	download_form = DownloadAccountForm()

	if request.method == "POST" and download_form.validate_on_submit():
		entered_pass = download_form.password.data

		# Check password is correct
		if not current_user.verify_password(entered_pass):
			flash("Current password was incorrect.", "danger")
			return redirect(url_for("user_bp.download"))
		else:
			# If user has re-entered password we can mark their session as fresh
			confirm_login()

		# Create the export
		user_data = {
			"time_created": current_user.time_created,
			"name": current_user.name,
			"email": current_user.email,
			"phone": current_user.phone,
			"active": current_user.active,
			"account_type": current_user.account_type,
		}

		def generate():
			for key in user_data.keys():
				yield f"{key}, "
			yield "\n"
			for value in user_data.values():
				yield f"{value}, "

		export_id = f'export_data_u0{current_user.id}_{time()}.csv'

		return Response(
			generate(),
			mimetype="text/plain",
			headers={"Content-Disposition": f"attachment;filename={export_id}"},
		)

	return render_template("download.html", dl_account=download_form)


@user_bp.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
	delete_form = DeleteAccountForm()

	if request.method == "POST" and delete_form.validate_on_submit():
		entered_pass = delete_form.password.data

		# Check password is correct
		if not current_user.verify_password(entered_pass):
			flash("Account password was incorrect.", "danger")
			return redirect(url_for("user_bp.delete"))

		# Find all users quizzes if they are a lecturer / admin
		if current_user.account_type > 2:
			qtd = Quiz.query.filter(
				Quiz.user_id == current_user.id
			).all()
			for q in qtd:
				qsl = QuizStream.query.filter(QuizStream.quiz_id == q.id).all()

				# Delete all quiz streams for that quiz
				for qs in qsl:
					db.session.delete(qs)

				# Remove that specific quiz
				db.session.delete(q)

		update_user = User.query.filter_by(id=current_user.id).first()
		db.session.delete(update_user)
		db.session.commit()

		logout_user()
		flash("Your account has been deleted.", "warning")
		return redirect(url_for("user_bp.clear_all"))

	return render_template("delete.html", delf=delete_form)
