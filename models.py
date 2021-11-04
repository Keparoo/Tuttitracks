"""Models for Spotiflavor"""

import os
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

if os.getenv('ENV') == 'test':
    database_path = os.getenv('TEST_DATABASE_URL')
else:
    database_path = os.getenv('DATABASE_URL')
    # Handle Heroku database URL
    if database_path.startswith('postgres://'):
        database_path = database_path.replace('postgres://', 'postgresql://', 1)

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database"""

    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True

    db.app = app
    db.init_app(app)
    print(f'Connecting to: {database_path}')

class User(db.Model):
    """Model for User class"""

    __tablename__ = 'users'

    username = db.Column(db.Text(25), primary_key=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.Text(50), nullable=False)
    spotify_user_id = db.Column(db.Text)
    spotify_display_name = db.Column(db.Text)
    user_image = db.Column(db.String)
    is_admin = db.Column(db.Boolean, nullable = False, default=False)
    current_market = db.Column(db.String(2), default='US')

    def __repr__(self):
        """Show info about a User"""

        return f"<User {self.username} {self.email} {self.is_admin} {self.current_market}>"

    def serialize(self):
        """Turn object into dictionary"""

        return {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "is_admin": self.is_admin,
            "current_market": self.current_market
        }

    @classmethod
    def register(cls, username, password, email, is_admin, current_market):
        """Register user with hashed password & return user"""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, is_admin=is_admin, current_market=current_market)

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # return user instance
            return user
        else:
            return False    

    @staticmethod
    def insert(user):
        """Insert user record into database"""

        db.session.add(user)
        db.session.commit()

    @staticmethod
    def update():
        """Update user record in database"""

        db.session.commit()

    @staticmethod
    def delete(user):
        """Delete user record from database"""

        db.session.delete(user)
        db.session.commit()

class Track(db.Model):
    """Model for music track class"""

    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spotify_track_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    spotify_track_url = db.Column(db.String, nullable=False)
    spotify_track_uri = db.Column(db.String, nullable=False)
    is_playable = db.Column(db.Boolean, nullable=False)
    preview_url = db.Column(db.String) # can be null
    release_year = db.Column(db.Integer, nullable=False)
    popularity = db.Column(db.Integer) # (0-100)
    duration = db.Column(db.Integer, nullable=False)

    acousticness = db.Column(db.Float) # (0.0-1.0)
    danceability = db.Column(db.Float) # (0.0-1.0)
    energy = db.Column(db.Float) # (0.0-1.0)
    instrumentalness = db.Column(db.Float) # (0.0-1.0)
    liveness = db.Column(db.Float) # (0.0-1.0)
    loudness = db.Column(db.Float) # (0.0-1.0)
    speechiness = db.Column(db.Float) # (0.0-1.0)
    valence = db.Column(db.Float) # (0.0-1.0)
    mode = db.Column(db.Integer) # (0=minor, 1=major)
    key = db.Column(db.Integer) # (0-11: 0=C, 1=D-flat/C-sharp, 11=B)
    time_signature = db.Column(db.Integer) # (number beats/measure)

    lyrics = db.Column(db.String)
    lyrics_language = db.Column(db.Text(2))

    def __repr__(self):
        """Show info about a Track"""

        return f"<Track {self.id} {self.name} {self.spotify_track_id} {self.spotify_track_uri}>"

class Playlist(db.Model):
    """Model for music track playlist class"""

    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.username'), nullable=False)
    spotify_playlist_id = db.Column(db.String)
    image = db.Column(db.String)
    public = db.Column(db.Boolean, default=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    def __repr__(self):
        """Show info about a Playlist"""

        return f"<Playlist {self.id} {self.user_id} {self.name} {self.description} {self.spotify_playlist_id}>"

class PlaylistTrack(db.Model):
    """Model joins playlists to tracks"""

    __tablename__ = 'playlists_tracks'

    # Playlists can have the same track in multiple slots
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=False)
    # Playlists need an order
    index = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        """Show info about playlist-track relationship"""

        return f"<PlaylistTrack {self.id} {self.playlist_id} {self.track_id} {self.index}>"

class Album(db.Model):
    """Model of music albums"""

    __tablename__ = 'albums'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spotify_album_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    image_height = db.Column(db.Integer, nullable=False) # may not be needed
    image_width = db.Column(db.Integer, nullable=False) # may not be needed

    def __repr__(self):
        """Show info about album"""

        return f"<Album {self.id} {self.name} {self.spotify_album_id}>"

class TrackAlbum(db.Model):
    """Model joins tracks to albums"""

    __tablename__ = 'tracks_albums'

    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"), primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey("albums.id"), primary_key=True)

    def __repr__(self):
        """Show info about track-album relationship"""

        return f"<TrackAlbum {self.track_id} {self.album_id}>"

class Artist(db.Model):
    """Model of music artists"""

    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spotify_artist_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        """Show info about Artist"""

        return f"<Artist {self.id} {self.name} {self.spotify_artist_id}>"

class TrackArtist(db.Model):
    """Model joins tracks to artists"""

    __tablename__ = 'tracks_artists'

    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), primary_key=True)

    def __repr__(self):
        """Show info about track-artist relationship"""

        return f"<TrackArtist {self.track_id} {self.artist_id}>"

class Genre(db.Model):
    """Model of music genres"""

    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        """Show info about Genre"""

        return f"<Genre {self.id} {self.name}>"

class TrackGenre(db.Model):
    """Model joins tracks to genres"""

    __tablename__ = 'tracks_genres'

    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), primary_key=True)

    def __repr__(self):
        """Show info about track-genre relationship"""

        return f"<TrackGenre {self.track_id} {self.genre_id}>"