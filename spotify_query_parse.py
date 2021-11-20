"""Spotify Query and Parse Functions"""

from models import db, Track, Album, Artist, TrackArtist
from auth import refresh_token
from flask import flash, redirect, g
import requests
from app import BASE_URL


#==================================================================================================
# Spotify Request Method
#==================================================================================================

def spotify_request(verb, url, data=None):
    """Request to spotify API with proper auth: refresh bearer token if necessary
    verb is the HTTP verb of the request: GET, POST, PUT, PATCH, DELETE
    Security headers are set on the g.headers variable
    For POST, PUT, PATCH and DELETE the optional data variable is used for body data
    """

    try:
        r = requests.request(verb, url=BASE_URL+url, headers=g.headers, data=data)

        # Token has expired: request refresh
        if r.status_code == 401:
            g.headers = refresh_token(g.refresh)
            r = requests.request(verb, url=BASE_URL+url, headers=g.headers, data=data)
    except:
        flash("Unable to connect to Spotify. Please try again later.", 'danger')
        return redirect ('/')

    return r

#==================================================================================================
# Spotify Search & Process Methods
#==================================================================================================

def get_spotify_track_ids(items):
    """Create list of found track ids from Spotify
    Currently not used
    """

    spot_track_ids = []
    for item in items:
        spot_track_ids.append(item['track']['id'])
    return spot_track_ids


def search_spotify(query_string, query_type, query_limit, offset):
    """Search Spotify, add matching tracks to db and return found tracks
    Called by /search
    """

    r = spotify_request('GET', f'/search?q={query_string}type={query_type}&limit={query_limit}&offset={offset}')

    tracks = process_tracks(r.json()['tracks']['items'])
    return tracks


def pre_process_tracks(found_tracks):
    """Pre-process json to remove leading ['track'] to prepare for process_search"""

    processed_tracks=[]
    for track in found_tracks:
        processed_tracks.append(track['track'])
    
    return processed_tracks


def get_spotify_liked_tracks(limit=25, offset=0):
    """ 
    Return a list of user's saved Spotify track objects and save to db
    Called by /tracks
    """
    
    r = spotify_request('GET', f'/me/tracks?limit={limit}&offset={offset}')

    processed_tracks = pre_process_tracks(r.json()['items'])
    tracks = process_tracks(processed_tracks)
    
    return tracks

def get_spotify_top_tracks(limit=25, offset=0, time_range='medium_term'):
    """ 
    Return a list of user's top Spotify track objects and save to db
    Called by /top
    """

    r = spotify_request('GET', f'/me/top/tracks?limit={limit}&offset={offset}&time_range={time_range}')

    tracks = process_tracks(r.json()['items'])
    
    return tracks

def process_tracks(found_tracks):
    """Check if db has each spotify track id
        This is to parse the /search route

        if spotify_track_id not found, create entry return id
        if spotify_track_id is found, return id
        return a list of ids (both found and created) from search
    """

    track_ids = []
    tracks = []
    for track in found_tracks:
        #Check if in db
        track_exists = Track.query.filter(Track.spotify_track_id==track['id']).first()

        #If yes, get id, append to track_ids[]
        if track_exists:
            tracks.append({"name": track_exists.name, "id": track_exists.id, "spotify_track_id": track_exists.spotify_track_id})

        #If no, populate db, append id to track_ids[]
        else:
            new_track = Track(
                spotify_track_id=track['id'],
                name=track['name'],
                popularity=track['popularity'],
                spotify_track_uri=track['uri'],
                release_year=track['album']['release_date'][:4],
                duration_ms=track['duration_ms'])
            
            # check if album in db, if so connect to track else create and connect
            album = Album.query.filter(Album.spotify_album_id==track['album']['id']).first()
            if album:
                new_track.album_id = album.id
            else:
                new_album = Album(
                    spotify_album_id = track['album']['id'],
                    name = track['album']['name'],
                    image = track['album']['images'][2]['url']
                )
                Album.insert(new_album)
                new_track.album_id = new_album.id
            Track.insert(new_track)

            tracks.append({"name": new_track.name, "id": new_track.id, "spotify_track_id": new_track.spotify_track_id})
            track_ids.append(new_track.id)

        if track_exists:
             track_id = track_exists.id
        else:
            track_id = new_track.id

        #loop through artists
        for artist in track['artists']:
            #Check if artist is in db
            artist_exists = Artist.query.filter(Artist.spotify_artist_id==artist['id']).first()

            #If artist is in db and track new
            if artist_exists:
                if not track_exists:
                    #connect existing artist to new track
                    new_track_artist = TrackArtist(track_id=track_id, artist_id=artist_exists.id)
                    db.session.add(new_track_artist)
                    db.session.commit()

            #Artist not in db: create new artist and link to track
            else:
                new_artist = Artist(
                    spotify_artist_id=artist['id'],
                    name=artist['name']
                )
                Artist.insert(new_artist)
                new_track_artist = TrackArtist(track_id=track_id, artist_id=new_artist.id)
                db.session.add(new_track_artist)
                db.session.commit()

    # Query Spotify database for audio features and populate db if any tracks are new
    if len(track_ids):
        get_audio_features(track_ids)

    return tracks


def create_track_list(track_ids):
    """Take a list of track_ids and return a comma separated list of spotify_track_ids
        Called by get_audio_features
    """

    tracks = ''
    for track in track_ids:
        track= Track.query.get(track)
        tracks += track.spotify_track_id + ','
    return tracks[:-1]
   

def get_audio_features(track_ids):
    """Take list of track_ids, query Spotify and populate db with audio features"""

    tracks = create_track_list(track_ids)

    r = spotify_request('GET', '/audio-features?ids=' + tracks)

    # Save audio features to db
    for track in r.json()['audio_features']:
        db_track = Track.query.filter(Track.spotify_track_id==track['id']).first()
        db_track.danceability = track['danceability']
        db_track.energy = track['energy']
        db_track.tempo = track['tempo']
        db_track.key = track['key']
        db_track.loudness = track['loudness']
        db_track.mode = track['mode']
        db_track.speechiness = track['speechiness']
        db_track.acousticness = track['speechiness']
        db_track.instrumentalness = track['acousticness']
        db_track.liveness = track['liveness']
        db_track.valence = track['valence']
        db_track.tempo = track['tempo']
        db_track.time_signature = track['time_signature']
        Track.update()