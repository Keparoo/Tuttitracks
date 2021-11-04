"""Spotiflavor Springboard Capstone 1"""

import os
import requests
from flask import Flask, render_template, request, redirect, flash, session, g
from sqlalchemy.exc import IntegrityError
# from flask_debugtoolbar import DebugToolbarExtension

from dotenv import load_dotenv

from models import db, connect_db, User, Track, Playlist, Album, Artist, Genre
from forms import SignupForm, LoginForm
from auth import requires_signed_in, requires_auth, requires_feedback_auth, requires_signed_out

load_dotenv()

# Spotify app client id and client secret
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

# Session key to determine logged in
CURR_USER_KEY = 'curr_user'

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['DEBUG'] = False
# toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

#====================================================================================
# User signnup/login/logout
#====================================================================================

@app.before_request
def add_user_to_g():
    """If user is logged in, add current user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user"""

    session[CURR_USER_KEY] = user.username


def do_logout():
    """Log out user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup"""

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                country=form.country.data,
                image_url=User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user"""

    do_logout()
    flash(f"Goodbye, {g.user.username}. You successfully logged out!", "success")
    return redirect('/login')

#====================================================================================
# Home Route
#====================================================================================

@app.route('/')
def homepage():
    """Display homepage"""



#====================================================================================
# error handlers
#====================================================================================

@app.errorhandler(404)
def resource_not_found(error):
    return render_template('/errors/404.html'), 404

@app.errorhandler(401)
def resource_not_found(error):
    return render_template('/errors/401.html'), 401

@app.errorhandler(403)
def resource_not_found(error):
    return render_template('/errors/403.html'), 403

@app.errorhandler(500)
def resource_not_found(error):
    return render_template('/errors/500.html'), 500