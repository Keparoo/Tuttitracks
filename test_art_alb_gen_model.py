"""Tests for Album, Artist, and Genre models"""

from unittest import TestCase

from app import app
from models import db, Track, Album, Artist, Genre, TrackArtist, TrackGenre
from flask import Flask, session
from sqlalchemy import exc

# Use test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spotiflavor_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

TEST_ALBUM_1 = {
    "spotify_album_id": "testspotifyalbumid1",
    "name": "testalbumname1",
    "image": "http://www.testimage.com"
}

TEST_ARTIST_1 = {
    "spotify_artist_id": "testspotifyartistid1",
    "name": "testartistname1"
}

TEST_GENRE_1 = {
    "name": "testgenrename1"
}

TEST_TRACK_1 = {
    "spotify_track_id": "testtrackid1",
    "name": "testname1",
    "spotify_track_uri": "testspotifytrackuri1",
    "duration_ms": 1000,
    "release_year": 1985,
    "album_id": 1
}

TEST_TRACK_2 = {
    "spotify_track_id": "testtrackid2",
    "name": "testname2",
    "spotify_track_uri": "testspotifytrackuri2",
    "duration_ms": 2000,
    "release_year": 1925,
    "album_id": 1
}

class PlaylistModelTestCase(TestCase):
    """Tests for playlist model"""

    def setUp(self): 
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        test_album = Album(
            spotify_album_id=TEST_ALBUM_1['spotify_album_id'],
            name=TEST_ALBUM_1['name'],
            image=TEST_ALBUM_1['image']
        )

        db.session.add(test_album)
        db.session.commit()
        self.album_id = 1

        test_artist = Artist(
            spotify_artist_id=TEST_ARTIST_1['spotify_artist_id'],
            name=TEST_ARTIST_1['name']
        )

        db.session.add(test_artist)
        db.session.commit()
        self.artist_id = 1

        test_genre = Genre(
            name=TEST_GENRE_1['name']
        )

        db.session.add(test_genre)
        db.session.commit()
        self.genre_id = 1


        test_track_1 = Track(
            spotify_track_id=TEST_TRACK_1['spotify_track_id'],
            name=TEST_TRACK_1['name'],
            spotify_track_uri=TEST_TRACK_1['spotify_track_uri'],
            release_year=TEST_TRACK_1['release_year'],
            duration_ms=TEST_TRACK_1['duration_ms'],
            album_id=self.album_id,
        )
        test_track_2 = Track(
            spotify_track_id=TEST_TRACK_2['spotify_track_id'],
            name=TEST_TRACK_2['name'],
            spotify_track_uri=TEST_TRACK_2['spotify_track_uri'],
            release_year=TEST_TRACK_2['release_year'],
            duration_ms=TEST_TRACK_2['duration_ms'],
            album_id=self.album_id,
        )

        db.session.add(test_track_1)
        db.session.commit()
        db.session.add(test_track_2)
        db.session.commit()
        self.track_1_id = 1
        self.track_2_id = 2

        test_track_artist = TrackArtist(
            track_id=self.track_1_id,
            artist_id=self.artist_id
        )

        db.session.add(test_track_artist)
        db.session.commit()
        self.track_artist_id=1

        test_track_genre = TrackGenre(
            track_id=self.track_1_id,
            genre_id=self.genre_id
        )

        db.session.add(test_track_genre)
        db.session.commit()
        self.track_artist_id=1

        
    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()

    #=======================================================================================
    # Album Model Tests    
    #=======================================================================================

    def test_album_repr_(self):

        test_album = Album.query.get(self.album_id)

        self.assertEqual(Album.__repr__(test_album), f"<Album {self.album_id} {TEST_ALBUM_1['name']} {TEST_ALBUM_1['spotify_album_id']}>")

    def test_spotify_album_id(self):
        """Test for valid spotify_album_id"""

        test_album = Album.query.get(self.album_id)

        self.assertEqual(test_album.spotify_album_id, TEST_ALBUM_1['spotify_album_id'])

    def test_album_name(self):
        """Test for valid name"""

        test_album = Album.query.get(self.album_id)

        self.assertEqual(test_album.name, TEST_ALBUM_1['name'])

    def test_album_image(self):
        """Test for valid image"""

        test_album = Album.query.get(self.album_id)

        self.assertEqual(test_album.image, TEST_ALBUM_1['image'])

    def test_album_to_track(self):
        """Test relationship from album to track"""

        test_album = Album.query.get(self.album_id)
        track = test_album.tracks[0]

        self.assertEqual(track.id, self.track_1_id)

    def test_track_to_album(self):
        """Test relationship from album to track"""

        test_track = Track.query.get(self.track_1_id)
        album = test_track.album

        self.assertEqual(album.id, self.album_id)

    #=======================================================================================
    # Artist Model Tests    
    #=======================================================================================

    def test_artist_repr_(self):
        """Test artist repr"""

        test_artist = Artist.query.get(self.artist_id)

        self.assertEqual(Artist.__repr__(test_artist), f"<Artist {self.artist_id} {TEST_ARTIST_1['name']} {TEST_ARTIST_1['spotify_artist_id']}>")

    def test_spotify_artist_id(self):
        """Test for valid spotify_album_id"""

        test_artist = Artist.query.get(self.artist_id)

        self.assertEqual(test_artist.spotify_artist_id, TEST_ARTIST_1['spotify_artist_id'])

    def test_artist_name(self):
        """Test for valid name"""

        test_artist = Artist.query.get(self.artist_id)

        self.assertEqual(test_artist.name, TEST_ARTIST_1['name'])

    def test_artist_to_track(self):
        """Test artist to track relationship"""

        test_artist = Artist.query.get(self.artist_id)
        track = test_artist.tracks[0]

        self.assertEqual(track.id, self.track_1_id)

    def test_track_to_artist(self):
        """Test track to artist relationship"""

        test_track = Track.query.get(self.track_1_id)
        artist = test_track.artists[0]

        self.assertEqual(artist.id, self.artist_id)      

    #=======================================================================================
    # Genre Model Tests    
    #=======================================================================================

    def test_genre_repr_(self):
        """Test genre repr"""

        test_genre = Genre.query.get(self.genre_id)

        self.assertEqual(Genre.__repr__(test_genre), f"<Genre {self.genre_id} {TEST_GENRE_1['name']}>")

    def test_genre_name(self):
        """Test for valid spotify_album_id"""

        test_genre = Genre.query.get(self.genre_id)

        self.assertEqual(test_genre.name, TEST_GENRE_1['name'])

    def test_genre_to_track(self):
        """Test genre to track relationship"""

        test_genre = Genre.query.get(self.genre_id)
        track = test_genre.tracks[0]

        self.assertEqual(track.id, self.track_1_id)

    def test_track_to_genre(self):
        """Test track to genre relationship"""

        test_track = Track.query.get(self.track_1_id)
        genre = test_track.genres[0]

        self.assertEqual(genre.id, self.genre_id)