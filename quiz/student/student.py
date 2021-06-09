from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, login_required
# from .forms import LoginForm
# from .models import db, User
from .. import login_manager
from is_safe_url import is_safe_url
from datetime import datetime

student_bp = Blueprint("student_bp", __name__, template_folder="templates", url_prefix="/s")


@student_bp.route("/dashboard")
def dashboard():
	return render_template('student/dashboard.html')
