"""Helper Functions for Spotiflavor"""

from re import M
from models import Track, Album, Artist, Genre, PlaylistTrack, TrackArtist, TrackGenre

def get_spotify_track_ids(items):
    """Create list of found track ids from Spotify"""

    spot_track_ids = []
    for item in items:
        spot_track_ids.append(item['track']['id'])
    return spot_track_ids

def process_track_search(spotify_track_ids):
    """Check if db has each spotify track id
        if spotify_track_id not found, create entry return id
        if spotify_track_id is found, return id
        return a list of ids (both found and created) from search
    """

    track_ids = []
    for track in spotify_track_ids:
        #Check if in db
        track_result = Track.query.filter(Track.spotify_track_id==track['id']).first()
        #If yes, get id, append to track_ids[]
        if track_result:
            track_ids.append(track_result.id)
        #If no, populate db, append id to track_ids[]
        else:
            new_track = Track(
                spotify_track_id=track['id'],
                name=track['name'],
                popularity=track['popularity'],
                spotify_track_url=track['external_urls']['spotify'],
                spotify_track_uri=track['uri'],
                is_playable=True,
                priview_url=track['preview_url'],
                release_year=track['id'],
                duration_ms=track['duration_ms'])
            # check if album in db, if so connect to track else create and connect
            album = Album.query.filter(Track.id==track['album']['id']).first()
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

            #loop through artists
            #if exists connect to track
            #if new create and connect to track

            #Genre
        
        
        

    return track_ids

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



def parse_tracks_items(obj):
    """Parse the object items of a search track request"""

    album = obj['album']
    artists = obj['artists']
    available_markets = obj['available_markets']
    disc_number = obj['disc_number']
    duration_ms = obj['duration_ms']
    explicit = obj['explicit']
    external_ids = obj['external_ids']
    external_urls = obj['external_urls']
    href = obj['href']
    id = obj['id']
    is_local = obj['is_local']
    name = obj['name']
    popularity = obj['popularity']
    preview_url = obj['preview_url']
    track_number = obj['track_number']
    type = obj['type']
    uri = obj['uri']

def parse_album_items(obj):
    """Parse the object items of a search album request"""

    album_type = obj['album_type']
    artists = obj['artists']
    available_markets = obj['available_markets']
    external_urls = obj['external_urls']
    href = obj['href']
    id = obj['id']
    images = obj['images'][0]['url']
    images = obj['images'][0]['height']
    images = obj['images'][0]['width']
    name = obj['name']
    release_date = obj['release_date']
    release_date_precision = obj['release_date_precision']
    total_tracks = obj['total_tracks']
    type = obj['type']
    uri = obj['uri']

def parse_artist_items(obj):
    """Parse the object items of a search artist"""


    external_urls = obj['external_urls']
    href = obj['href']
    id = obj['id']
    name = obj['name']
    type = obj['type']
    uri = obj['uri']
