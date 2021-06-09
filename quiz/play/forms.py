from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class JoinGameForm(FlaskForm):
	game_code = StringField('Game Code', validators=[DataRequired(message='Please enter a game code')])
	submit = SubmitField('Join Game')
