"""Helper Functions for Spotiflavor"""

import json
from models import db, Track, Album, Artist, TrackArtist, Playlist, PlaylistTrack
from auth import refresh_token
from flask import g
import requests

BASE_URL = 'https://api.spotify.com/v1'


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

    headers = {
        'Authorization': f'Bearer {g.token}'
    }

    r = requests.get(BASE_URL + '/search' + f'?q={query_string}type={query_type}&limit={query_limit}&offset={offset}', headers=headers)

    # Token has expired: request refresh
    if r.status_code == 401:
        headers = refresh_token(g.refresh)
        r = requests.get(BASE_URL + '/search' + f'?q={query_string}type={query_type}&limit={query_limit}&offset={offset}', headers=headers)

    tracks = process_search(r.json()['tracks']['items'])
    return (tracks)


def get_spotify_saved_tracks(limit=25, offset=0):
    """ 
    Return a list of user's saved Spotify track objects and save to db
    Called by /tracks
    """

    headers = {
        'Authorization': f'Bearer {g.token}'
    }
    
    r = requests.get(BASE_URL + f'/me/tracks?limit={limit}&offset={offset}', headers=headers)
    
    # Token has expired: request refresh
    if r.status_code == 401:
        headers = refresh_token(g.refresh)
        r = requests.get(BASE_URL + f'/me/tracks?limit={limit}', headers=headers)
    
    tracks = process_track_search(r.json()['items'])
    
    return (tracks)


def process_track_search(found_tracks):
    """Check if db has each spotify track id
        This is to process the /tracks route

        if spotify_track_id not found, create entry return id
        if spotify_track_id is found, return id
        return a list of ids (both found and created) from search
    """

    track_ids = []
    track_dicts = []
    for track in found_tracks:
        #Check if in db
        track_exists = Track.query.filter(Track.spotify_track_id==track['track']['id']).first()

        #If yes, get id, append to track_ids[]
        if track_exists:
            track_dicts.append({"name": track_exists.name, "id": track_exists.id, "spotify_track_id": track_exists.spotify_track_id})
            track_ids.append(track_exists.id)

        #If no, populate db, append id to track_ids[]
        else:
            new_track = Track(
                spotify_track_id=track['track']['id'],
                name=track['track']['name'],
                popularity=track['track']['popularity'],
                spotify_track_uri=track['track']['uri'],
                release_year=track['track']['album']['release_date'][:4],
                duration_ms=track['track']['duration_ms'])
            
            # check if album in db, if so connect to track else create and connect
            album = Album.query.filter(Album.spotify_album_id==track['track']['album']['id']).first()
            if album:
                new_track.album_id = album.id
            else:
                new_album = Album(
                    spotify_album_id = track['track']['album']['id'],
                    name = track['track']['album']['name'],
                    image = track['track']['album']['images'][2]['url']
                )
                Album.insert(new_album)
                new_track.album_id = new_album.id
            Track.insert(new_track)

            track_dicts.append({"name": new_track.name, "id": new_track.id, "spotify_track_id": new_track.spotify_track_id})
            track_ids.append(new_track.id)

        if track_exists:
             track_id = track_exists.id
        else:
            track_id = new_track.id

        #loop through artists
        for artist in track['track']['artists']:
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

    # Query Spotify database for audio features and populate db
    get_audio_features(track_ids)
    
    return track_dicts     


def process_search(found_tracks):
    """Check if db has each spotify track id
        This is to parse the /search route

        if spotify_track_id not found, create entry return id
        if spotify_track_id is found, return id
        return a list of ids (both found and created) from search
    """

    track_ids = []
    track_dicts = []
    for track in found_tracks:
        #Check if in db
        track_exists = Track.query.filter(Track.spotify_track_id==track['id']).first()
        #If yes, get id, append to track_ids[]
        if track_exists:
            track_dicts.append({"name": track_exists.name, "id": track_exists.id, "spotify_track_id": track_exists.spotify_track_id})
            track_ids.append(track_exists.id)

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

            track_dicts.append({"name": new_track.name, "id": new_track.id, "spotify_track_id": new_track.spotify_track_id})
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

    # Query Spotify database for audio features and populate db
    get_audio_features(track_ids)

    return track_dicts


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

    headers = {
    'Authorization': f'Bearer {g.token}'
    }

    tracks = create_track_list(track_ids)

    r = requests.get(BASE_URL + '/audio-features?ids=' + tracks, headers=headers)

    # Token has expired: request refresh
    if r.status_code == 401:
        headers = refresh_token(g.refresh)
        r = requests.get(BASE_URL + '/audio-features?ids=' + tracks, headers=headers)

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


#====================================================================================
# API CRUD methods
#====================================================================================

def create_playlist(name="New Playlist", description=None, tracks=[], public=True):
    """Create a working playlist locally"""

    new_playlist = Playlist(
        username = g.user.username,
        name = name,
        description = description,
        public = public,
        collaborative = False # Can only be True if public is False
    )
    Playlist.insert(new_playlist)

    index = 0
    for track in tracks:
        new_playlist_track = PlaylistTrack(
            playlist_id = new_playlist.id,
            track_id = track,
            index = index
        )
        PlaylistTrack.insert(new_playlist_track)
        index += 1

    return new_playlist


def get_playlist_tracks(playlist_id):
    """
    Get the current tracks from a local playlist
    Return a list of spotify uris in index order
    """

    playlist_tracks = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id).order_by(PlaylistTrack.index).all()

    spotify_uris = []
    for item in playlist_tracks:
        track = Track.query.get_or_404(item.track_id)
        spotify_uris.append(track.spotify_track_uri)

    return spotify_uris


def get_playlist_track_ids(playlist_id):
    """Get the current tracks from a local playlist
    Return a list of spotify ids in index order
    """

    playlist_tracks = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id).order_by(PlaylistTrack.index).all()

    spotify_ids = []
    for item in playlist_tracks:
        track = Track.query.get_or_404(item.track_id)
        spotify_ids.append(track.spotify_track_id)

    return spotify_ids


def append_playlist_tracks(playlist_id, track_ids):
    """Append a list of track ids to existing playlist"""

    last_track = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id).order_by(PlaylistTrack.index.desc()).first()
    if last_track:
        index = last_track.index + 1
    else:
        index = 0
    
    for track in track_ids:
        new_playlist_track = PlaylistTrack(
            playlist_id = playlist_id,
            track_id = track,
            index = index
        )
        PlaylistTrack.insert(new_playlist_track)
        index += 1


def insert_playlist_track(playlist_id, track_id, index):
    """Insert a track into an existing playlist"""

    # Check current user owns playlist

    playlist_tracks = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id, PlaylistTrack.index >= index).order_by(PlaylistTrack.index).all()

    for track in playlist_tracks:
        track.index += 1
    new_playlist_track = PlaylistTrack(
        playlist_id = playlist_id,
        track_id = track_id,
        index = index
    )
    PlaylistTrack.insert(new_playlist_track)


def move_playlist_track(playlist_id, track_id, new_index):
    """Move a playlist track from its current index to a new index"""

    track_to_move = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id, PlaylistTrack.track_id==track_id).first()
    current_index = track_to_move.index
    if new_index > current_index:
        
        tracks = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id, PlaylistTrack.index > current_index).order_by(PlaylistTrack.index).all()
        for track in tracks:
            if track.index <= new_index:
                track.index -= 1
        track_to_move.index = new_index

    else:
        tracks = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id, PlaylistTrack.index >= new_index).order_by(PlaylistTrack.index).all()
        
        for track in tracks:
            if track.index <= current_index:
                track.index += 1
        track_to_move.index = new_index

    PlaylistTrack.update()
    

def delete_playlist_track(playlist_id, track_id):
    """Delete a track from a playlist"""

    track = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id, PlaylistTrack.track_id==track_id).first()
    index = track.index
    PlaylistTrack.delete(track)

    tracks_after = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id, PlaylistTrack.index > index).order_by(PlaylistTrack.index).all()
    for track in tracks_after:
        track.index -= 1
    PlaylistTrack.update()


def get_playlist_item_info(playlists):
    """Parse playlist item info, return list of dicts"""

    playlist_info = []
    for playlist in playlists:
        name = playlist['name']
        description = playlist['description']
        spotify_playlist_id = playlist['id']
        snapshot_id = playlist['snapshot_id']
        num_tracks = playlist['tracks']['total']
        public = playlist['public']
        collaborative = playlist['collaborative']
        owner = playlist['owner']['display_name']

        playlist_info.append({"name": name, "description": description, "spotify_playlist_id": spotify_playlist_id, "snapshot_id": snapshot_id, "num_tracks": num_tracks, "public": public, "collborative": collaborative, "owner": owner})

    return playlist_info


#==================================================================================================
# Spotify Playlist Crud Methods
#==================================================================================================

def get_spotify_playlists(limit=20, offset=0):
    """Retrieve current users' playlists"""

    headers = {
        'Authorization': f'Bearer {g.token}'
    }

    r = requests.get(BASE_URL + f'/me/playlists?limit={limit}&offset={offset}', headers=headers)

    # Token has expired: request refresh
    if r.status_code == 401:
        headers = refresh_token(g.refresh)
        r = requests.get(BASE_URL + f'/me/playlists?limit={limit}&offset={offset}', headers=headers)

    # print(r.text)
    return r.json()


def create_spotify_playlist(playlist_id):
    """Create a new playlist on Spotify server from local playlist id"""

    headers = {
        'Authorization': f'Bearer {g.token}'
    }

    playlist = Playlist.query.get_or_404(playlist_id)

    data = {
        "name": playlist.name,
        "description": playlist.description,
        "public": playlist.public, #Defaults to True
        "collaborative": playlist.collaborative #Defaults to False, can only be true when public is False
    }
    r = requests.post(BASE_URL + f'/users/{g.user.spotify_user_id}/playlists', headers=headers, data=json.dumps(data))

    # Token has expired: request refresh
    if r.status_code == 401:
        headers = refresh_token(g.refresh)
        r = requests.post(BASE_URL + f'/users/{g.user.spotify_user_id}/playlists', headers=headers, data=json.dumps(data))
    
    #Update local playlist object with spotify_playlist_id and image if available
    playlist.spotify_playlist_id = r.json()['id']
    playlist.spotify_snapshot_id = r.json()['snapshot_id']
    if r.json()['images']:
        playlist.image = r.json()['images'][0]['url']
    Playlist.update()

    return playlist


def add_tracks_to_spotify_playlist(spotify_playlist_id, spotify_uri_list=[], position=None):
    """
    Add tracks to an existing Spotify playlist

    Given a list of spotify_uris to add in the following form. Max: 100 uris
    ["spotify:track:0wipEzrv6p17BPiVCKATIE", "spotify:track:2Amj13n8K8JRaSNXh2C10G", ...]

    Optional position arg is 0 based index of where to insert uris. Default is to append.

    Returns snapshot_id of playlist
    """

    headers = {
        'Authorization': f'Bearer {g.token}'
    }
    data = {
        "uris": spotify_uri_list,
        "position": position #Optional, Defaults to append
    }

    r = requests.post(BASE_URL + f'/playlists/{spotify_playlist_id}/tracks', headers=headers, data=json.dumps(data))

    # Token has expired: request refresh
    if r.status_code == 401:
        headers = refresh_token(g.refresh)
        r = requests.post(BASE_URL + f'/playlists/{spotify_playlist_id}/tracks', headers=headers, data=json.dumps(data))

    playlist = Playlist.query.filter(Playlist.spotify_playlist_id==spotify_playlist_id)
    playlist.spotify_snapshot_id = r.json()['snapshot_id']
    Playlist.update()

    return playlist


def replace_spotify_playlist_items(spotify_playlist_id, spotify_uri_list=[]):
    """
    Replace all current tracks with new tracks, same tracks in new order, both or an empty playlist

    Given a list of spotify_uris to remove in the following form. Max: 100 uris
    ["spotify:track:0wipEzrv6p17BPiVCKATIE", "spotify:track:2Amj13n8K8JRaSNXh2C10G", ...]

    Sending an empty list will clear the entire playlist yielding an empty playlist

    Returns the snapshot_id of the playlist
    """

    headers = {
        'Authorization': f'Bearer {g.token}'
    }
    data = {
        "uris": spotify_uri_list
    }

    r = requests.put(BASE_URL + f'/playlists/{spotify_playlist_id}/tracks', headers=headers, data=json.dumps(data))

    # Token has expired: request refresh
    if r.status_code == 401:
        headers = refresh_token(g.refresh)
        r = requests.put(BASE_URL + f'/playlists/{spotify_playlist_id}/tracks', headers=headers, data=json.dumps(data))

    playlist = Playlist.query.filter(Playlist.spotify_playlist_id==spotify_playlist_id)
    playlist.spotify_snapshot_id = r.json()['snapshot_id']
    Playlist.update()

    return playlist


def delete_tracks_from_spotify_playlist(spotify_playlist_id, spotify_uri_list=[]):
    """
    Delete tracks from a spotify playlist

    Given a list of spotify_uris to remove in the following form. Max: 100 uris
    [{"uri":"spotify:track:0wipEzrv6p17BPiVCKATIE"}, {"uri:"spotify:track:2Amj13n8K8JRaSNXh2C10G"}, ...]

    Returns snapshot_id of playlist
    """

    headers = {
        'Authorization': f'Bearer {g.token}'
    }
    data = {
        "tracks": spotify_uri_list
    }

    r = requests.delete(BASE_URL + f'/playlists/{spotify_playlist_id}/tracks', headers=headers, data=json.dumps(data))

    # Token has expired: request refresh
    if r.status_code == 401:
        headers = refresh_token(g.refresh)
        r = requests.delete(BASE_URL + f'/playlists/{spotify_playlist_id}/tracks', headers=headers, data=json.dumps(data))

    playlist = Playlist.query.filter(Playlist.spotify_playlist_id==spotify_playlist_id)
    playlist.spotify_snapshot_id = r.json()['snapshot_id']
    Playlist.update()

    return playlist


def update_spotify_playlist_details(spotify_playlist_id, name, description, public, collaborative):
    """
    Update the details of a spotify playlist
    collborative can only be set to True on non-public playlists
    """

    headers = {
        'Authorization': f'Bearer {g.token}'
    }
    data = {
        "name": name,
        "description": description,
        "public": public,
        "collaborative": collaborative
    }

    r = requests.put(BASE_URL + f'/playlists/{spotify_playlist_id}', headers=headers, data=json.dumps(data))

    # Token has expired: request refresh
    if r.status_code == 401:
        headers = refresh_token(g.refresh)
        r = requests.put(BASE_URL + f'/playlists/{spotify_playlist_id}', headers=headers, data=json.dumps(data))

    return r.status_code

