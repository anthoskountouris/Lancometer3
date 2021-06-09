from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields.html5 import EmailField, TelField


class SignupForm(FlaskForm):
	name = StringField(label="Name", validators=[DataRequired(
		message="Everyone has a name."), Length(min=2, message="Username's too short.")])
	email = EmailField(label='Email', validators=[Email(
		message='Enter a valid email.'), DataRequired(message="We'll need to be in touch.")])
	password = PasswordField(label='Password', validators=[DataRequired(
		message="We need to make sure it's you!"), Length(min=8, message='Select a stronger password.')])
	confirm = PasswordField(label='Confirm password', validators=[DataRequired(
		message="Don't forget to confirm your password!"), EqualTo('password', message='Passwords must match.')])
	phone = TelField(label="Phone number", validators=[Length(min=7, message="Phone number is too short.")], render_kw={
		'pattern': '^[+]?[0-9]{9,12}$', 'oninvalid': 'this.setCustomValidity("Phone Number must be in international format. e.g +441234567890")', 'oninput': 'this.setCustomValidity("")'})
	# terms = BooleanField(label='terms', validators=[DataRequired(message="Make sure you've read this!")])


class LoginForm(FlaskForm):
	email = EmailField(label='Email', validators=[DataRequired(message="Who are you again?"), Email(message='Enter a valid email.')])
	password = PasswordField(label='Password', validators=[DataRequired("That doesn't seem right.")])


class ReAuthUserForm(FlaskForm):
	password = PasswordField('Account Password', validators=[DataRequired(message='Please enter your password')])
	submit = SubmitField('Re-Authenticate')


class UpdatePasswordForm(FlaskForm):
	old_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=8, max=255)])
	new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=255)])
	confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
	submit = SubmitField('Update Password')


class UpdateEmailForm(FlaskForm):
	new_email = EmailField('New Email', validators=[DataRequired(), Email(message='Enter a valid email.')])
	password = PasswordField('Account Password', validators=[DataRequired(message='You must enter your account password'), Length(min=8, max=255)])
	submit = SubmitField('Update Email')


class DownloadAccountForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=255)])
	submit = SubmitField('Download')


class DeleteAccountForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=255)])
	submit = SubmitField('Delete')
