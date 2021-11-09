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

#==================================================================================================
# User Model
#==================================================================================================

class User(db.Model):
    """Model for User class"""

    __tablename__ = 'users'

    username = db.Column(db.String(25), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    spotify_user_id = db.Column(db.Text)
    spotify_display_name = db.Column(db.Text)
    user_image = db.Column(db.Text, default="/static/images/default-pic.png")
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    refresh_token = db.Column(db.Text)
    country = db.Column(db.String(2), default='US')

    # playlists = db.relationship('Playlist', back_populates='user', cascade='delete-orphan')

    def __repr__(self):
        """Show info about a User"""

        return f"<User {self.username} {self.email} {self.country} {self.spotify_user_id} {self.spotify_display_name} {self.is_admin}>"

    def serialize(self):
        """Turn object into dictionary"""

        return {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "spotify_user_id": self.spotify_user_id,
            "spotify_display_name": self.spotify_display_name,
            "user_image": self.user_image,
            "is_admin": self.is_admin,
            "country": self.country
        }

    @classmethod
    def signup(cls, username, password, email, country, user_image):
        """Register user with hashed password & return user"""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, country=country, user_image=user_image)

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

#==================================================================================================
# Track Model
#==================================================================================================

class Track(db.Model):
    """Model for music track class"""

    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spotify_track_id = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    spotify_track_url = db.Column(db.Text, nullable=False)
    spotify_track_uri = db.Column(db.Text, nullable=False)
    # is_playable = db.Column(db.Boolean, nullable=False)
    preview_url = db.Column(db.Text) # can be null
    release_year = db.Column(db.Integer, nullable=False)
    popularity = db.Column(db.Integer) # (0-100)
    duration = db.Column(db.Integer, nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'))

    album = db.relationship('Album', backref='tracks', cascade='delete, merge, save-update')



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

    lyrics = db.Column(db.Text)
    lyrics_language = db.Column(db.String(2))

    def __repr__(self):
        """Show info about a Track"""

        return f"<Track {self.id} {self.name} {self.spotify_track_id} {self.spotify_track_uri}>"

    @staticmethod
    def insert(track):
        """Insert track record into database"""

        db.session.add(track)
        db.session.commit()

    @staticmethod
    def update():
        """Update track record in database"""

        db.session.commit()

    @staticmethod
    def delete(track):
        """Delete track record from database"""

        db.session.delete(track)
        db.session.commit()

#==================================================================================================
# Playlist Models
#==================================================================================================

class Playlist(db.Model):
    """Model for music track playlist class"""

    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(25), db.ForeignKey('users.username'), nullable=False)
    spotify_playlist_id = db.Column(db.Text)
    image = db.Column(db.Text)
    public = db.Column(db.Boolean, default=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)


    # delete: delete playlist if user is deleted
    user = db.relationship('User', backref='playlists', cascade='delete, merge, save-update')

    def __repr__(self):
        """Show info about a Playlist"""

        return f"<Playlist {self.id} {self.user_id} {self.name} {self.description} {self.spotify_playlist_id}>"

    @staticmethod
    def insert(playlist):
        """Insert playlist record into database"""

        db.session.add(playlist)
        db.session.commit()

    @staticmethod
    def update():
        """Update playlist record in database"""

        db.session.commit()

    @staticmethod
    def delete(playlist):
        """Delete playlist record from database"""

        db.session.delete(playlist)
        db.session.commit()

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

#==================================================================================================
# Album, Artist, Genre Models
#==================================================================================================

class Album(db.Model):
    """Model of music albums"""

    __tablename__ = 'albums'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spotify_album_id = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    # image_height = db.Column(db.Integer, nullable=False)
    # image_width = db.Column(db.Integer, nullable=False)

    # tracks = db.relationship('Track', back_populates='album', cascade='delete-orphan')

    def __repr__(self):
        """Show info about album"""

        return f"<Album {self.id} {self.name} {self.spotify_album_id}>"

    @staticmethod
    def insert(album):
        """Insert album record into database"""

        db.session.add(album)
        db.session.commit()

    @staticmethod
    def update():
        """Update album record in database"""

        db.session.commit()

    @staticmethod
    def delete(album):
        """Delete album record from database"""

        db.session.delete(album)
        db.session.commit()

# In case a many to many is needed. Currently I think album to track is one to many
# class TrackAlbum(db.Model):
#     """Model joins tracks to albums"""

#     __tablename__ = 'tracks_albums'

#     track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"), primary_key=True)
#     album_id = db.Column(db.Integer, db.ForeignKey("albums.id"), primary_key=True)

#     def __repr__(self):
#         """Show info about track-album relationship"""

#         return f"<TrackAlbum {self.track_id} {self.album_id}>"

class Artist(db.Model):
    """Model of music artists"""

    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spotify_artist_id = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)

    tracks = db.relationship('Track', secondary='tracks_artists', backref='artists')

    def __repr__(self):
        """Show info about Artist"""

        return f"<Artist {self.id} {self.name} {self.spotify_artist_id}>"

    @staticmethod
    def insert(artist):
        """Insert artist record into database"""

        db.session.add(artist)
        db.session.commit()

    @staticmethod
    def update():
        """Update artist record in database"""

        db.session.commit()

    @staticmethod
    def delete(artist):
        """Delete artist record from database"""

        db.session.delete(artist)
        db.session.commit()

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
    name = db.Column(db.Text, nullable=False)

    tracks = db.relationship('Track', secondary='tracks_genres', backref='genres')

    def __repr__(self):
        """Show info about Genre"""

        return f"<Genre {self.id} {self.name}>"

    @staticmethod
    def insert(genre):
        """Insert genre record into database"""

        db.session.add(genre)
        db.session.commit()

    @staticmethod
    def update():
        """Update genre record in database"""

        db.session.commit()

    @staticmethod
    def delete(genre):
        """Delete genre record from database"""

        db.session.delete(genre)
        db.session.commit()

class TrackGenre(db.Model):
    """Model joins tracks to genres"""

    __tablename__ = 'tracks_genres'

    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), primary_key=True)

    def __repr__(self):
        """Show info about track-genre relationship"""

        return f"<TrackGenre {self.track_id} {self.genre_id}>"