from os import path, makedirs
from flask_login import login_required
from hashids import Hashids
from .forms import UploadForm
from flask import (Blueprint, render_template, current_app, redirect, url_for)
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload_bp", __name__, template_folder="templates")
hashids = Hashids(min_length=8, salt=current_app.secret_key)

if not path.exists(current_app.config['UPLOADED_FILES_DEST']):
	makedirs(current_app.config['UPLOADED_FILES_DEST'])


@upload_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
	form = UploadForm()

	if form.validate_on_submit():
		for file in form.file.data:
			filename = secure_filename(file.filename)
			file.save(path.join(
				current_app.config['UPLOADED_FILES_DEST'], filename
			))
		return redirect(url_for('upload_bp.upload_file'))

	return render_template('uploads.html', title="Upload Files", form=form)
