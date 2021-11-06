"""Spotiflavor Springboard Capstone 1"""

import os
import json
import requests
from flask import Flask, render_template, request, redirect, flash, session, g
from sqlalchemy.exc import IntegrityError
# from flask_debugtoolbar import DebugToolbarExtension

from dotenv import load_dotenv

from models import db, connect_db, User, Track, Playlist, Album, Artist, Genre
from forms import SignupForm, LoginForm, SearchTracksForm
from auth import requires_signed_in, requires_auth, requires_feedback_auth, requires_signed_out

load_dotenv()

# Spotify app client id and client secret
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
BASE_URL = 'https://api.spotify.com/v1/'
ACCESS_TOKEN = 'BQCFZ3LPLq1EFYRnhuI_Eo8mqsZfs_A4ZDUiXdXnPf_pqjs2XWdOReLu-LHGG_s2IRgvJjWNZKblu1Ko095S8cjFzT_uSggHdc7XFI-oAHMhOo0EVxIPlgva9FKRHJ1ONgBiV-n3eFcvmNsmu74daXLVy-OXpG15a_4'

HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# Session key assigned to user object if user is logged in
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
                country=form.country.data or User.country.default.arg,
                user_image=User.user_image.default.arg,
            )
            User.insert(user)

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

    return render_template('homepage.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Display form to search and post on successful submit"""

    form = SearchTracksForm()

    if form.validate_on_submit():

        query = {

        "artist": form.artist.data,
        "track":form.track.data,
        "album": form.album.data,
        "genre": form.genre.data,
        "playlist": form.playlist.data,
        # "year": form.year.data,
        "new": form.new.data,
        "hipster": form.hipster.data
        }

        track_id="6y0igZArWVi6Iz0rj35c1Y"

        artist = query['artist']
        # r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=HEADERS)
        r = requests.get(BASE_URL + 'search' + f'?q={artist}&type=album,track&limit=5', headers=HEADERS)
        # r = r.json()
        r = r.text
        # id = r['albums']['items'][0]['id']
        # print(id)

        return render_template("/results.html", query=query, r=r)

    else:
        return render_template('/search.html', form=form)

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