"""Helper Functions for Spotiflavor"""

import json
from models import db, Track, Album, Artist, TrackArtist, Playlist, PlaylistTrack, Genre, TrackGenre
from flask import session, g
import requests

BASE_URL = 'https://api.spotify.com/v1'

def get_spotify_track_ids(items):
    """Create list of found track ids from Spotify"""

    spot_track_ids = []
    for item in items:
        spot_track_ids.append(item['track']['id'])
    return spot_track_ids

def process_track_search(found_tracks):
    """Check if db has each spotify track id
        if spotify_track_id not found, create entry return id
        if spotify_track_id is found, return id
        return a list of ids (both found and created) from search
    """

    track_ids = []
    for track in found_tracks:
        #Check if in db
        track_exists = Track.query.filter(Track.spotify_track_id==track['track']['id']).first()
        #If yes, get id, append to track_ids[]
        if track_exists:
            track_ids.append(track_exists.id)
        #If no, populate db, append id to track_ids[]
        else:
            new_track = Track(
                spotify_track_id=track['track']['id'],
                name=track['track']['name'],
                popularity=track['track']['popularity'],
                spotify_track_url=track['track']['external_urls']['spotify'],
                spotify_track_uri=track['track']['uri'],
                preview_url=track['track']['preview_url'],
                release_year=track['track']['album']['release_date'][:4],
                duration=track['track']['duration_ms'])
            
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

    get_audio_features(track_ids)
            
    return track_ids

def create_track_list(track_ids):
    """Take a list of track_ids and return a comma separated list of spotify_track_ids"""

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

    for track in r.json()['audio_features']:
        db_track = Track.query.filter(Track.spotify_track_id==track['id']).first()
        db_track.danceability = track['danceability']
        db_track.energy = track['energy']
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

def create_playlist(name="New Playlist", description=None, public=True, tracks=[]):
    """Create a working playlist locally"""

    new_playlist = Playlist(
        username = g.user.username,
        name = name,
        description = description,
        public = public
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

#==================================================================================================
# Spotify Playlist Crud Methods
#==================================================================================================

def create_spotify_playlist(playlist_id):
    """Create a new playlist on Spotify server from local playlist id"""

    headers = {
        'Authorization': f'Bearer {g.token}'
    }

    playlist = Playlist.query.get(playlist_id)

    data = {
        "name": playlist.name,
        "description": playlist.description,
        "public": playlist.public #Defaults to True
        # "collaborative": False #Defaults to False
    }
    r = requests.post(BASE_URL + f'/users/{g.user.spotify_user_id}/playlists', headers=headers, data=json.dumps(data))
    
    #Update local playlist object with spotify_playlist_id and image if available
    playlist.spotify_playlist_id = r.json()['id']
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

    return r.json()['snapshot_id']

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

    return r.json()['snapshot_id']

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

    return r.json()['snapshot_id']

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

    return r.status_code

#==================================================================================================
# Parsing Methods
#==================================================================================================

def parse_search(obj):
    """parse a returned search object and return the values"""

    href = obj['href']
    items = obj['items']
    limit = obj['limit']
    next = obj['next']
    offset = obj['offset']
    previous = obj['previous']
    total = obj['total']

    print('HREF', obj['href'])

    return {
        obj['href']
    }
