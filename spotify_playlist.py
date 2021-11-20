"""Spotify playlist management methods"""

import json
from models import Playlist
from flask import g
from spotify_query_parse import spotify_request

#==================================================================================================
# Spotify Playlist CRUD Methods
#==================================================================================================

def get_spotify_playlists(limit=20, offset=0):
    """Retrieve current users' playlists"""

    r = spotify_request('GET', f'/me/playlists?limit={limit}&offset={offset}')

    return r.json()


def create_spotify_playlist(playlist_id):
    """Create a new playlist on Spotify server from local playlist id"""

    playlist = Playlist.query.get_or_404(playlist_id)

    data = {
        "name": playlist.name,
        "description": playlist.description,
        "public": playlist.public, #Defaults to True
        "collaborative": playlist.collaborative #Defaults to False, can only be true when public is False
    }

    r = spotify_request('POST', f'/users/{g.user.spotify_user_id}/playlists', data=json.dumps(data))
    
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

    data = {
        "uris": spotify_uri_list,
        "position": position #Optional, Defaults to append
    }

    r = spotify_request('POST', f'/playlists/{spotify_playlist_id}/tracks', data=json.dumps(data))

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

    data = {
        "uris": spotify_uri_list
    }

    r = spotify_request('PUT', f'/playlists/{spotify_playlist_id}/tracks', data=json.dumps(data))

    playlist = Playlist.query.filter(Playlist.spotify_playlist_id==spotify_playlist_id)
    playlist.spotify_snapshot_id = r.json()['snapshot_id']
    Playlist.update()

    return playlist


def update_spotify_playlist_details(spotify_playlist_id, name, description, public, collaborative):
    """
    Update the details of a spotify playlist
    collborative can only be set to True on non-public playlists
    """

    data = {
        "name": name,
        "description": description,
        "public": public,
        "collaborative": collaborative
    }

    r = spotify_request('PUT', f'/playlists/{spotify_playlist_id}', data=json.dumps(data))

    return r.status_code


def delete_tracks_from_spotify_playlist(spotify_playlist_id, spotify_uri_list=[]):
    """
    Delete tracks from a spotify playlist

    Given a list of spotify_uris to remove in the following form. Max: 100 uris
    [{"uri":"spotify:track:0wipEzrv6p17BPiVCKATIE"}, {"uri:"spotify:track:2Amj13n8K8JRaSNXh2C10G"}, ...]

    Returns snapshot_id of playlist
    """

    data = {
        "tracks": spotify_uri_list
    }


    r = spotify_request('DELETE', f'/playlists/{spotify_playlist_id}/tracks', data=json.dumps(data))

    playlist = Playlist.query.filter(Playlist.spotify_playlist_id==spotify_playlist_id)
    playlist.spotify_snapshot_id = r.json()['snapshot_id']
    Playlist.update()

    return playlist