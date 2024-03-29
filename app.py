"""Tuttitracks: Spotify track information gatherer and playlist editor"""

import os
from flask import Flask, render_template, request, redirect, flash, session, g, jsonify
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError
# from flask_debugtoolbar import DebugToolbarExtension

from dotenv import load_dotenv

BASE_URL = 'https://api.spotify.com/v1'

# Session key assigned to user object if user is logged in
CURR_USER_KEY = 'curr_user'

from models import db, connect_db, User, Track, Playlist
from forms import SignupForm, LoginForm, SearchTracksForm, ChangePasswordForm
from auth import get_spotify_user_code, get_bearer_token
from middleware import requires_signed_in
from db_api_methods import create_playlist, get_playlist_tracks, get_playlist_track_ids, append_playlist_tracks, insert_playlist_track, move_playlist_track, delete_playlist_track, get_playlist_item_info
from spotify_playlist import get_spotify_playlists, create_spotify_playlist, add_tracks_to_spotify_playlist, replace_spotify_playlist_items, update_spotify_playlist_details, delete_tracks_from_spotify_playlist
from spotify_query_parse import get_spotify_liked_tracks, search_spotify, get_spotify_top_tracks

load_dotenv()

# Spotify app client id and client secret
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

BASE_URL = 'https://api.spotify.com/v1'

REDIRECT_URI = os.environ.get('REDIRECT_URI')



app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.app_context().push()
# app.config['DEBUG'] = False
# toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

#====================================================================================
# User signup/login/logout
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
        g.headers = {
        'Authorization': f'Bearer {g.token}'
    }
    else:
        g.token = None
        g.headers = None

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
    if 'auth' in session:
        del session['auth']
    if 'refresh' in session:
        del session['refresh']


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

    return render_template('homepage.html')


@app.route('/users/<username>')
@requires_signed_in
def user_page(username):
    """User info"""

    if username != g.user.username:
        flash(f"Unauthorized", "danger")
        return redirect('/')

    return render_template('users/user.html', username=username)

@app.route('/users/<username>/password', methods=['GET', 'POST'])
@requires_signed_in
def change_password(username):
    """Display form to change password. Post new password if credentials valid"""

    form = ChangePasswordForm()

    if form.validate_on_submit():
        user = User.authenticate(g.user.username,
                                 form.current_password.data)

        if user:
            new_password = form.new_password.data
            user.update_password(new_password)

            flash(f"{user.username}'s password successfully changed!", "success")
            return redirect(f'/users/{user.username}')

        flash("Password incorrect!", 'danger')

    return render_template('users/password.html', form=form)

#====================================================================================
# View Routes
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

        QUERY_LIMIT = 15
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
        tracks = search_spotify(query_string, QUERY_TYPE, QUERY_LIMIT, OFFSET)

        # Display nothing rather than None in query results
        if not query['year']:
            query['year'] = ""

        return render_template("results.html", query=query, tracks=tracks)

    else:
        return render_template('search.html', form=form)


@app.get('/tracks')
@requires_signed_in
def get_liked_tracks():
    """Query Spotify for user's liked tracks"""

    LIMIT = 25
    OFFSET = 0

    tracks = get_spotify_liked_tracks(limit=LIMIT, offset=OFFSET)

    return render_template("liked_tracks.html", tracks=tracks)


@app.get('/top')
@requires_signed_in
def get_top_tracks():
    """Query Spotify for user's top tracks"""

    LIMIT = 20
    OFFSET = 0
    # time_range is the time frame top tracks are calculated:
    # long_term=several years including new data as available, medium_term=approx 6 months (Spotify default), short_term=approx 4 weeks
    TIME_RANGE = 'medium_term'

    tracks = get_spotify_top_tracks(limit=LIMIT, offset=OFFSET, time_range=TIME_RANGE)

    return render_template("top_tracks.html", tracks=tracks)


@app.get('/playlists')
@requires_signed_in
def playlist_management():
    """Display local and Spotify playlists"""

    # Get local playlists
    playlists = Playlist.query.filter(Playlist.username==g.user.username).all()

    # Get spotify playlists
    LIMIT = 25
    OFFSET = 0
    spot_playlists = get_spotify_playlists(LIMIT, OFFSET)
    total_spot_playlists = spot_playlists['total']
    parsed_playlists = get_playlist_item_info(spot_playlists['items'])

    return render_template("playlists.html", playlists=playlists, spot_playlists=parsed_playlists, total_spot_playlists=total_spot_playlists)

#====================================================================================
# Database api routes
#====================================================================================

def get_track_ids(tracks):
    track_ids = []
    for track in tracks:
        track_ids.append(track['id'])
    return track_ids


def get_key_signature(key):
    """Convert key_signature number to readable key signature"""

    keys = ['C', 'D-flat', 'D', 'E-flat', 'E', 'F', 'G-flat', 'G', 'A-flat', 'A', 'B-flat', 'B']
 
    return keys[key]


def convert_ms(m_seconds):
    """Convert milliseconds to minutes and seconds"""

    minutes = str(m_seconds//60000)
    seconds = str(round(((m_seconds / 1000) % 60), 2))
    return f'{minutes}m {seconds}s'

# get user's playlists: GET /users/<user_id>/playlists

@app.get('/api/me/tracks')
def get_saved_tracks_route():
    """Get Spotify saved tracks for current user"""

    offset = request.args.get('offset', 0)

    try:
        tracks = get_spotify_liked_tracks(offset=offset, limit=25)
        
        return jsonify({
            'success': True,
            'track_dicts': tracks,
            'tracks': tracks
        }), 200

    except:
        
        return jsonify({
            'success': False,
            'message': "Unable to fetch Spotify saved tracks"
        }), 404


@app.get('/api/me/top/tracks')
def get_top_tracks_route():
    """Get Spotify top tracks for current user"""

    offset = request.args.get('offset', 0)
    limit = request.args.get('offset', 20)
    time_range = request.args.get('time_range', 'medium-term')

    get_spotify_top_tracks(limit=25, offset=0, time_range='medium_term')

    try:
        tracks = get_spotify_top_tracks(limit=limit, offset=offset, time_range=time_range)
        
        return jsonify({
            'success': True,
            'tracks': tracks
        }), 200

    except:
        
        return jsonify({
            'success': False,
            'message': "Unable to fetch Spotify top tracks"
        }), 404

@app.get('/api/tracks/<int:track_id>')  
def get_audio_features_route(track_id):
    """Get the audio features of a track from database"""

    try:
        track = Track.query.get_or_404(track_id)

        key_signature = get_key_signature(int(track.key))
        mode = "Major" if track.mode else "minor"
        duration = convert_ms(int(track.duration_ms))

        return jsonify({
            'success': True,
            'name': track.name,
            'popularity': track.popularity,
            'release_year': track.release_year,
            'album': track.album.name,
            'duration': duration,
            'acousticness': track.acousticness,
            'danceability': track.danceability,
            'energy': track.energy,
            'tempo': track.tempo,
            'instrumentalness': track.instrumentalness,
            'key': key_signature,
            'liveness': track.liveness,
            'loudness': track.loudness,
            'mode': mode,
            'speechiness': track.speechiness,
            'time_signature': track.time_signature,
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
def get_my_playlists():
    """Get current users playlists: return list of playlist objects"""

    try:
        playlists = Playlist.query.filter(Playlist.username==g.user.username)
        
        return jsonify({
            'success': True,
            'playlists': playlists
        }), 200
    
    except:
        print(g.user.username)
        return jsonify({
            'success': False,
            'message': "Unable to get playlists"
        }), 404


@app.get('/api/playlists/<int:playlist_id>')
def get_playlist(playlist_id):
    """Get and return a playlist object"""

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
def get_playlist_track_ids_route(playlist_id):
    """Get playlist tracks: return list of spotify track ids"""

    print('get_playlist_track_ids')
    try:
        tracks = get_playlist_track_ids(playlist_id)
        print(tracks)
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
def append_playlist_tracks_route(playlist_id):
    """Append tracks to playlist in db"""

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


@app.patch('/api/playlists/<playlist_id>/track')
def move_playlist_track_route(playlist_id):
    """Move a playlist track to a new position"""

    current_index = request.json['current_index']
    new_index = request.json['new_index']

    try:
        move_playlist_track(playlist_id, current_index, new_index)
        return jsonify({
            'success': True,
            'playlist': playlist_id
        }), 200
    except:
        return jsonify({
            'success': False,
            'message': "Unable to move track"
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
    """Delete a track from a playlist in database"""

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


@app.post('/api/spotify/<int:id>/playlists')
def update_playlist_to_spotify(id):
    """Create new playlist on Spotify from local playlist
        If playlist already exists, replace existing tracks on Spotify with current tracks from database
    """

    try:
        playlist =  Playlist.query.get_or_404(id)
        tracks = get_playlist_tracks(id)

        # Create Spotify playlist and add tracks
        if not playlist.spotify_playlist_id:
            print('New Playlist')
            new_playlist = create_spotify_playlist(id)
            replace_spotify_playlist_items(new_playlist.spotify_playlist_id, tracks)
        else:
            # Playlist alread exists on Spotify, update tracks only
            print('Playlist exists')
            replace_spotify_playlist_items(playlist.spotify_playlist_id, tracks)

        return jsonify({
            'success': True,
            'playlist': playlist.serialize()
        }), 200

    except:
        return jsonify({
            'success': False,
            'message': "Unable to create spotify playlist"
        }), 404


@app.get('/api/spotify/playlists')
def get_spotify_playlists_route():
    """Get current user's spotify playlists"""

    limit = request.args.get('limit', 20)
    offset = request.args.get('offset', 0)

    try:
        playlists = get_spotify_playlists(limit, offset)
        total_spot_playlists = playlists['total']
        parsed_playlists = get_playlist_item_info(playlists['items'])

        return jsonify({
            "success": True,
            "spot_playlists": parsed_playlists,
            "total_spot_playlists": total_spot_playlists
        }), 200

    except:
        return jsonify({
            "success": False,
            "message": "Unable to retrieve playlists"
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