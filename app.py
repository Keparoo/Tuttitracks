"""Spotiflavor Springboard Capstone 1"""

import os
import json
import base64
import requests
from flask import Flask, render_template, request, redirect, flash, session, g, jsonify
from sqlalchemy.exc import IntegrityError
# from flask_debugtoolbar import DebugToolbarExtension

from dotenv import load_dotenv

from models import db, connect_db, User, Track, Playlist, Album, Artist, Genre
from forms import SignupForm, LoginForm, SearchTracksForm
from auth import get_spotify_user_code, get_bearer_token, requires_signed_in, refresh_token, requires_auth, requires_signed_out
from helpers import create_playlist, create_spotify_playlist, get_spotify_track_ids, process_track_search, parse_search, add_tracks_to_spotify_playlist,delete_tracks_from_spotify_playlist,replace_spotify_playlist_items,update_spotify_playlist_details, get_spotify_saved_tracks, get_spotify_playlists, get_playlist_tracks, insert_playlist_track, append_playlist_tracks, delete_playlist_track, move_playlist_track, search_spotify

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
    else:
        g.token = None

    if 'refresh' in session:
        g.refresh = session['refresh']
    else:
        g.refresh = None


def do_login(user):
    """Log in user"""

    session[CURR_USER_KEY] = user.username


def do_logout():
    """Log out user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        del session['auth']

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
    # User code to obtain bearer token
    auth = get_bearer_token(code)

    if 'error' in auth:
        flash(f"Error: {auth['error']} {auth['error_description']}", "danger")
        print('Error: ', auth['error'], auth['error_description'])
    else:
        session['auth'] = auth
        session['refresh'] = auth['refresh_token']
  
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

    headers = {
        'Authorization': f'Bearer {g.token}'
    }

    # track1 = "6, 0wipEzrv6p17BPiVCKATIE, Gnossienne Nr. 1, spotify:track:0wipEzrv6p17BPiVCKATIE"
    # track2 = '7, 2Amj13n8K8JRaSNXh2C10G, Pure Imagination (from "Charlie and the Chocolate Factory"), spotify:track:2Amj13n8K8JRaSNXh2C10G'
    # track3 = '8, 7ma87nv4jgpXfjlwMFOvLn, Allez donc vous faire bronzer, spotify:track:7ma87nv4jgpXfjlwMFOvLn'
    # track4 = '9, 4qqf1avpzRUnVowNQd1jFw, Zou bisou bisou, spotify:track:4qqf1avpzRUnVowNQd1jFw'

    # track_id="2Amj13n8K8JRaSNXh2C10G"
    # r = requests.get(BASE_URL + '/audio-features/' + track_id, headers=HEADERS)
    # r = requests.get(BASE_URL + '/search' + f'?q={artist}&type=track&limit=25', headers=headers)
    
    # Get users saved tracks
    # tracks = get_spotify_saved_tracks(limit=25)

    # playlists = get_spotify_playlists(limit=20, offset=0)
    # print(playlists)

    #Create playlist
    # playlist = create_spotify_playlist(1)
    # print(playlist)

    # To test:
    # playlist = create_spotify_playlist(1)
    # print(playlist)

    # spotify_uri_list = get_playlist_tracks(1)
    # spotify_uri_list = [{'uri':'spotify:track:3cTX97kSfqIs9U68fOjIEB'}]
    # print(spotify_uri_list)
    # add_tracks_to_spotify_playlist('5gprcPiOPACeLyPB0y6MkE', spotify_uri_list)
    # replace_spotify_playlist_items('5gprcPiOPACeLyPB0y6MkE', spotify_uri_list)
    # delete_tracks_from_spotify_playlist('5gprcPiOPACeLyPB0y6MkE', spotify_uri_list)
    # update_spotify_playlist_details('5gprcPiOPACeLyPB0y6MkE', 'Spotiflavor Playlist', 'This is a groovy new playlist brought to you by Spotiflavor', True, False)

    # insert_playlist_track(1, 25, 2)
    # append_playlist_tracks(1, [9, 10])
    # delete_playlist_track(1, 25)
    # move_playlist_track(1, 8, 4)
    # playlist = Playlist.query.get(1)
    # Playlist.delete(playlist)
    # new_playlist = create_playlist("Spotiflavor Playlist", "This is a groovy new playlist brought to you by Spotiflavor", True, [7, 8, 9, 1])
    # print(new_playlist)

    # tracks = r.json()['tracks']['items']
    # r = r.text
    # print(r)
    # r=1

    # return render_template("/results.html", query=query, r=r)

    return render_template('homepage.html')

#====================================================================================
# Search Routes
#====================================================================================

def create_query(artist, track, album, genre, year):
    """Create a query string from passed in query filters"""

    query = ''
    if artist:
        query += f'artist:{artist}&'
    if track:
        query += f'track:{track}&'
    if album:
        query += f'album:{album}&'
    if genre:
        query += f'genre:{genre}&'
    if year:
        query += f'year{year}&'

    return query
    

@app.route('/search', methods=['GET', 'POST'])
@requires_signed_in
def search():
    """Display form to search and post on successful submit"""

    form = SearchTracksForm()

    if form.validate_on_submit():

        # insert_playlist_track(1, 25, 2)
        # append_playlist_tracks(1, [9, 10])
        # delete_playlist_track(1, 25)
        # move_playlist_track(1, 8, 4)
        # playlist = Playlist.query.get(1)
        # Playlist.delete(playlist)
        # new_playlist = create_playlist("Spotiflavor Playlist", "This is a groovy new playlist brought to you by Spotiflavor", True, [7, 8, 9, 1])
        # print(new_playlist)

        QUERY_LIMIT = 10
        QUERY_TYPE = 'track'
        OFFSET = 0

        query = {
            "artist": form.artist.data,
            "track":form.track.data,
            "album": form.album.data,
            "genre": form.genre.data,
            "year": form.year.data
            # "playlist": form.playlist.data,
            # "new": form.new.data,
            # "hipster": form.hipster.data
        }

        artist = form.artist.data
        track = form.track.data
        album = form.album.data
        genre = form.genre.data
        year = form.year.data

        # Empty search form
        if not artist and not track and not album and not genre and not year:
            year = 2021

        query_string = create_query(artist, track, album, genre, year)
        tracks, r = search_spotify(query_string, QUERY_TYPE, QUERY_LIMIT, OFFSET)

        # tracks = r.json()['tracks']['items']
        # r = r.text
        # print(r)
        # r=1

        # return render_template("/results.html", query=query, r=r)
        return render_template("results.html", query=query, tracks=tracks, r=r)

    else:
        return render_template('search.html', form=form)

@app.route('/tracks', methods=['GET'])
@requires_signed_in
def get_tracks():
    """Query Spotify for Users' saved tracks"""

    track_dicts, tracks = get_spotify_saved_tracks(limit=30)

    return render_template("display_tracks.html", tracks=tracks, track_dicts=track_dicts)

#====================================================================================
# Database api routes
#====================================================================================

def get_track_ids(tracks):
    track_ids = []
    for track in tracks:
        track_ids.append(track['id'])
    return track_ids

def get_key_signature(key):
    """Change number to readable key signature"""

    keys = ['C', 'D-flat', 'D', 'E-flat', 'E', 'F', 'G-flat', 'G', 'A-flat', 'A', 'B-flat', 'B']
 
    return keys[key]

# get user's playlists: GET /users/<user_id>/playlists
# update playlist details: PUT /playlists/<playlist_id>
# get track features: GET /tracks/<track_id>

@app.get('/api/tracks/<int:track_id>')  
def get_audio_features_route(track_id):
    """Get the audio features of a track from database"""

    try:
        track = Track.query.get_or_404(track_id)

        key_signature = get_key_signature(int(track.key))
        print(key_signature)
        mode = "Major" if track.mode else "minor"

        return jsonify({
            'success': True,
            'name': track.name,
            'popularity': track.popularity,
            'release_year': track.release_year,
            'album': track.album.name,
            'duration_ms': track.duration_ms,
            'acousticness': track.acousticness,
            'danceability': track.danceability,
            'energy': track.energy,
            'instrumentalness': track.instrumentalness,
            'key': key_signature,
            'liveness': track.liveness,
            'loudness': track.loudness,
            'mode': mode,
            'speechiness': track.speechiness,
            'time_signature': track.time_signature,
            # 'tempo': track.tempo,
            'valence': track.valence
        })
    except:
        return jsonify({
            'success': False,
            'message': "Track not found"
        }), 404


@app.post('/api/users/<username>/playlists')
def create_playlist_route(username):
    """Create a playlist locally"""

    name = request.json['name']
    description = request.json['description']
    tracks = request.json['playlistTracks']
    print('New Playlist & Tracks: ', name, description, tracks)

    try:
        track_ids = get_track_ids(tracks)
        # print(track_ids)
    except:
        return jsonify({
            'success': False,
            'message': "Unable to parse tracks"
        }), 404

    try:
        playlist = create_playlist(name, description, track_ids)
        print('New Playlist id:', playlist.id)

        return jsonify({
            'success': True,
            'name': name,
            'description': description, 
            'playlist_id': playlist.id
        }), 200

    except:
        return jsonify({
            'success': False,
            'message': "Unable to create playlist"
        }), 404

@app.put('/api/playlists/<int:playlist_id>')
def update_playlist_details_route(playlist_id):
    """Update playlist name or description"""

    name = request.json['name']
    description = request.json['description']
    print('New Playlist: ', name, description)

    try:
        playlist = Playlist.query.get_or_404(playlist_id)
        playlist.name = name
        playlist.description = description
        Playlist.update()

        return jsonify({
            'success': True,
            'name': playlist.name,
            'description': playlist.description, 
            'playlist_id': playlist_id
        }), 200

    except:
        return jsonify({
            'success': False,
            'message': "Unable to update playlist details",
        }), 404

@app.get('/api/me/playlists')
def get_my_playlists(username):
    """Get current users playlists"""

    try:
        playlists = Playlist.query.filter(Playlist.username==g.user.username)
        return jsonify({
            'success': True,
            'playlists': playlists
        }), 200

    except:
        return jsonify({
            'success': False,
            'message': "Unable to get playlists"
        }), 404

@app.get('/api/playlists/<int:playlist_id>')
def get_playlist(playlist_id):
    """Get a playlist"""

    try:
        playlist = Playlist.query.get_or_404(playlist_id)
        return jsonify({
            'success': True,
            'playlist': playlist
        }), 200

    except:
        return jsonify({
            'success': False,
            'message': "Unable to get playlist"
        }), 404 

@app.get('/api/playlists/<int:playlist_id>/tracks')
def get_playlist_items(playlist_id):
    """Get playlist tracks return list of track uris"""

    try:
        tracks = Playlist.query.get_or_404(playlist_id)
        return jsonify({
            'success': True,
            'tracks': tracks
        }), 200

    except:
        return jsonify({
            'success': False,
            'message': "Unable to get playlist tracks"
        }), 404      

@app.post('/api/playlists/<int:playlist_id>/tracks')
def add_tracks_to_playlist(playlist_id):
    """Add tracks to playlist"""

    track_ids = request.json['id']

    try:
        append_playlist_tracks(playlist_id, track_ids)

        return jsonify({
            'success': True,
            'playlist': playlist_id,
            'deleted': track_ids
        }), 200

    except:
        return jsonify({
            'success': False,
            'message': "Unable to add tracks"
        }), 404

@app.put('/api/playlists/<playlist_id>/tracks')
def update_playlist_tracks(playlist_id):
    """Replace current tracks with new list of tracks"""

    tracks = request.json['tracks']

    try:
        playlist = Playlist.query.get_or_404(playlist_id)
        replace_spotify_playlist_items(playlist.spotify_playlist_id, tracks)
        return jsonify({
            'success': True,
            'playlist': playlist_id
        }), 200

    except:
        return jsonify({
            'success': False,
            'message': "Unable to replace tracks"
        }), 404    

@app.patch('/api/playlists/<int:playlist_id>/tracks')
def delete_playlist_track_route(playlist_id):
    """Delete a track from a playlist"""

    track_id = request.json['id'][0]

    try:
        delete_playlist_track(playlist_id, track_id)
        return jsonify({
             'success': True,
            'playlist': playlist_id,
            'deleted': track_id
         }), 200
    except:
        return jsonify({
            'success': False,
            'message': "Unable to delete"
         }), 404


@app.delete('/api/playlists/<int:playlist_id>')
def delete_playlist_route(playlist_id):
    """Delete a playlist"""

    try:
        playlist = Playlist.query.get_or_404(playlist_id)
        Playlist.delete(playlist)

        return jsonify({
            'success': True,
            'deleted': playlist_id,
        }), 200
    except:
        return jsonify({
            'success': False,
            'message': "Playlist not found or not available"
        }), 404


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

#====================================================================================
# Turn off all caching in Flask -- DEV only: comment out when in production
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
#====================================================================================

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req