"""Database API CRUD methods"""

from models import Track, Playlist, PlaylistTrack
from flask import g

#====================================================================================
# Database API CRUD methods
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


# def move_playlist_track(playlist_id, track_id, new_index):
#     """Move a playlist track from its current index to a new index
#     given a track_id and index
#      This is currently not used. The start and end index version has replaced it
# """

#     track_to_move = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id, PlaylistTrack.track_id==track_id).first()
#     current_index = track_to_move.index
#     if new_index > current_index:
        
#         tracks = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id, PlaylistTrack.index > current_index).order_by(PlaylistTrack.index).all()
#         for track in tracks:
#             if track.index <= new_index:
#                 track.index -= 1
#         track_to_move.index = new_index

#     else:
#         tracks = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id, PlaylistTrack.index >= new_index).order_by(PlaylistTrack.index).all()
        
#         for track in tracks:
#             if track.index <= current_index:
#                 track.index += 1
#         track_to_move.index = new_index


def move_playlist_track(playlist_id, current_index, new_index):
    """Move a playlist track from its current index to a new index"""

    track_to_move = PlaylistTrack.query.filter(PlaylistTrack.playlist_id==playlist_id,PlaylistTrack.index==current_index).first()

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