"""Spotiflavor Springboard Capstone 1"""

import os
import json
import base64
import requests
from flask import Flask, render_template, request, redirect, flash, session, g
from sqlalchemy.exc import IntegrityError
# from flask_debugtoolbar import DebugToolbarExtension

from dotenv import load_dotenv

from models import db, connect_db, User, Track, Playlist, Album, Artist, Genre
from forms import SignupForm, LoginForm, SearchTracksForm
from auth import get_spotify_user_code, get_bearer_token, requires_signed_in, requires_auth, requires_signed_out
from helpers import create_playlist, create_spotify_playlist, get_spotify_track_ids, process_track_search, parse_search, add_tracks_to_spotify_playlist,delete_tracks_from_spotify_playlist,replace_spotify_playlist_items,update_spotify_playlist_details, get_spotify_saved_tracks, get_spotify_playlists, get_playlist_tracks

load_dotenv()

# Spotify app client id and client secret
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

# AUTH_URL = 'https://accounts.spotify.com/authorize'
# TOKEN_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1'

REDIRECT_URI = os.environ.get('REDIRECT_URI')

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

    if 'auth' in session:
        g.token = session['auth']['access_token']
        g.refresh = session['auth']['refresh_token']
    else:
        g.token = None
        g.refresh = None


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

        # Get Spotify user code needed to request bearer token
        redirect_url = get_spotify_user_code()
        # redirect to oath url asking user permission to log into spotify
        return redirect(redirect_url)

        # return redirect("/")

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

            # Get Spotify user code needed to request bearer token
            redirect_url = get_spotify_user_code()
            # redirect to oath url asking user permission to log into spotify
            return redirect(redirect_url)

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/authorize', methods=['GET'])
def get_auth_token():
    """Get auth token from query string"""

    # Get Spotify user code from redirected request get_spotify_user_code()
    code = request.args.get('code')
    auth = get_bearer_token(code)

    # message = f"{CLIENT_ID}:{CLIENT_SECRET}"
    # messageBytes = message.encode('ascii')
    # base64Bytes = base64.b64encode(messageBytes)
    # base64Message = base64Bytes.decode('ascii')

    # headers = {
    #     "Content-Type": "application/x-www-form-urlencoded",
    #     "Authorization": f"Basic {base64Message}"
    # }

    # data = {
    #     "code": code,
    #     "redirect_uri": REDIRECT_URI,
    #     "grant_type": "authorization_code"
    # }
    
    # r = requests.post(TOKEN_URL, headers=headers, data=data)

    # if 'error' in r.json():
    #     flash(f"Auth Error: {r.json()['error']} {r.json()['error_description']}", "danger")
    #     print('Auth Error: ', r.json()['error'], r.json()['error_description'])
    # else:
    #     auth = {
    #         "access_token": r.json()['access_token'],
    #         "token_type": r.json()['token_type'],
    #         "scope": r.json()['scope'],
    #         "expires_in": r.json()['expires_in'],
    #         "refresh_token": r.json()['refresh_token'],
    #         }
    if 'error' in auth:
        flash(f"Error: {auth['error']} {auth['error_description']}", "danger")
        print('Error: ', auth['error'], auth['error_description'])
    else:
        session['auth'] = auth
  
    return redirect('/')


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
@requires_signed_in
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

        headers = {
            'Authorization': f'Bearer {g.token}'
        }

        track1 = "6, 0wipEzrv6p17BPiVCKATIE, Gnossienne Nr. 1, spotify:track:0wipEzrv6p17BPiVCKATIE"
        track2 = '7, 2Amj13n8K8JRaSNXh2C10G, Pure Imagination (from "Charlie and the Chocolate Factory"), spotify:track:2Amj13n8K8JRaSNXh2C10G'
        track3 = '8, 7ma87nv4jgpXfjlwMFOvLn, Allez donc vous faire bronzer, spotify:track:7ma87nv4jgpXfjlwMFOvLn'
        track4 = '9, 4qqf1avpzRUnVowNQd1jFw, Zou bisou bisou, spotify:track:4qqf1avpzRUnVowNQd1jFw'

        artist = query['artist']
        # track_id="6y0igZArWVi6Iz0rj35c1Y"
        # r = requests.get(BASE_URL + '/audio-features/' + track_id, headers=HEADERS)
        # r = requests.get(BASE_URL + '/search' + f'?q={artist}&type=track&limit=5', headers=HEADERS)

        # Get users saved tracks
        tracks = get_spotify_saved_tracks(limit=25)

        # playlists = get_spotify_playlists(limit=20, offset=0)
        # print(playlists)


        # new_playlist = create_playlist("Spotiflavor Playlist", "This is a groovy new playlist brought to you by Spotiflavor", True, [7, 8, 9, 1])
        # print(new_playlist)

        #Create playlist
        # playlist = create_spotify_playlist(1)
        # print(playlist)

        # To test:
        # playlist = create_spotify_playlist(1)
        # print(playlist)

        # spotify_uri_list = get_playlist_tracks(1)
        spotify_uri_list = [{'uri':'spotify:track:3cTX97kSfqIs9U68fOjIEB'}]
        print(spotify_uri_list)
        # add_tracks_to_spotify_playlist('5gprcPiOPACeLyPB0y6MkE', spotify_uri_list)
        # replace_spotify_playlist_items('5gprcPiOPACeLyPB0y6MkE', spotify_uri_list)
        # delete_tracks_from_spotify_playlist('5gprcPiOPACeLyPB0y6MkE', spotify_uri_list)

        update_spotify_playlist_details('5gprcPiOPACeLyPB0y6MkE', 'Spotiflavor Playlist', 'This is a groovy new playlist brought to you by Spotiflavor', True, False)
        

        # r = r.json()
        # r = r.text
        r=1

        # return render_template("/results.html", query=query, r=r)
        return render_template("/results.html", query=query, r=r, tracks=tracks)

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