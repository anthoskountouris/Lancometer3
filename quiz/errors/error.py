from flask import Blueprint, request, abort, jsonify, render_template

error_bp = Blueprint('errors', __name__, template_folder="templates")


@error_bp.app_errorhandler(400)
def handle_400(err):
	if request.path.startswith('/api/'):
		return '{}'
	else:
		return render_template('errors/400.html', description=err), 400


@error_bp.app_errorhandler(403)
def handle_404(err):
	if request.path.startswith('/api/'):
		return '{}'
	else:
		return render_template('errors/403.html', description=err), 403


@error_bp.app_errorhandler(404)
def handle_404(err):
	if request.path.startswith('/api/'):
		return '{}'
	else:
		return render_template('errors/404.html', description=err), 404\


@error_bp.app_errorhandler(429)
def handle_429(err):
	if request.path.startswith('/api/'):
		return '{"error":true}'
	else:
		return render_template('errors/429.html', description=err), 429


@error_bp.app_errorhandler(500)
def handle_500(err):
	return render_template('errors/500.html'), 500
