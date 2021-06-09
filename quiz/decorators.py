from functools import wraps
from flask import request, abort
from flask_login import current_user


def internally_referred(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if request.referrer is None:
			return abort(400, description='Request invalid. No HTTP Referer sent')

		if request.host not in request.referrer:
			return abort(400, description='Request source disallowed')

		return f(*args, **kwargs)

	return decorated_function


def requires_account_type(account_type=0):
	def real_decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if current_user.account_type < account_type:
				return abort(403, description='No')
			return f(*args, **kwargs)
		return decorated_function
	return real_decorator
