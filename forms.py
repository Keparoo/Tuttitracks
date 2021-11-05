"""Spotiflavor Forms"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.fields.core import BooleanField
from wtforms.validators import InputRequired, Email, Length

class SignupForm(FlaskForm):
    """Form for registering a new user"""

    username = StringField("User Name", validators=[InputRequired(), Length(min=3, max=25, message="Username must be between 8 and 25 characters long.")], render_kw={'autofocus': True})
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(min=1, max=50, message="Email cannot be longer than 50 characters.")])
    country = StringField("Country Code", validators=[InputRequired(), Length(min=2, max=2, message="Country codes are exactly 2 characters long.")])

class LoginForm(FlaskForm):
    """Form for logging in user"""

    username = StringField("User Name", validators=[InputRequired()], render_kw={'autofocus': True})
    password = PasswordField("Password", validators=[InputRequired()])

class PlaylistForm(FlaskForm):
    """Form to create playlist"""

    name = StringField("Name of playlist", validators=[InputRequired()])
    description = TextAreaField("Description of playlist", validators=[InputRequired()])
    public = BooleanField("Is playlist public?")