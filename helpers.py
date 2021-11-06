"""Helper Functions for Spotiflavor"""

def parse_search(obj):
    """parse a returned search object and return the values"""

    href = obj['href']
    items = obj['href']
    limit = obj['href']
    next = obj['href']
    offset = obj['href']
    previous = obj['href']
    total = obj['href']

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
