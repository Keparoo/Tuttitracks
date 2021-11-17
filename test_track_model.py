"""Tests for Track model"""

from unittest import TestCase

from app import app
from models import db, Track, Album
from flask import Flask, session
from sqlalchemy import exc

# Use test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spotiflavor_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

TEST_TRACK_1 = {
    "spotify_track_id": "testtrackid1",
    "name": "testname1",
    "spotify_track_uri": "testspotifytrackuri1",
    "release_year": 1985,
    
    "duration_ms": 1000,
    "album_id": 1,
    "popularity": 50,
    "acousticness": .5,
    "danceability": .5,
    "energy": .5,
    "tempo": 50.1,
    "instrumentalness": .5,
    "liveness": .5,
    "loudness": -20.5,
    "speechiness": .5,
    "valence": .5,
    "mode": 0,
    "key": 3,
    "time_signature": 4,
    "lyrics": "test lyrics 1"
}

TEST_ALBUM_1 = {
    "spotify_album_id": "testspotifyalbumid1",
    "name": "testalbumname1",
    "image": "http://www.testimage.com"
}

class TrackModelTestCase(TestCase):
    """Tests for track model"""

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

        test_track = Track(
            spotify_track_id=TEST_TRACK_1['spotify_track_id'],
            name=TEST_TRACK_1['name'],
            spotify_track_uri=TEST_TRACK_1['spotify_track_uri'],
            release_year=TEST_TRACK_1['release_year'],
            duration_ms=TEST_TRACK_1['duration_ms'],
            album_id=self.album_id,

            popularity=TEST_TRACK_1['popularity'],
            acousticness=TEST_TRACK_1['acousticness'],
            danceability=TEST_TRACK_1['danceability'],
            energy=TEST_TRACK_1['energy'],
            tempo=TEST_TRACK_1['tempo'],
            instrumentalness=TEST_TRACK_1['instrumentalness'],
            liveness=TEST_TRACK_1['liveness'],
            loudness=TEST_TRACK_1['loudness'],
            speechiness=TEST_TRACK_1['speechiness'],
            valence=TEST_TRACK_1['valence'],
            mode=TEST_TRACK_1['mode'],
            key=TEST_TRACK_1['key'],
            time_signature=TEST_TRACK_1['time_signature'],
            lyrics=TEST_TRACK_1['lyrics']
        )
        db.session.add(test_track)
        db.session.commit()
        self.track_id = 1

        
    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()

    #=======================================================================================
    # Track Model Tests    
    #=======================================================================================

    def test_track__repr__(self):

        test_track = Track.query.get(self.track_id)

        self.assertEqual(Track.__repr__(test_track), f"<Track {self.track_id} {TEST_TRACK_1['name']} {TEST_TRACK_1['spotify_track_id']} {TEST_TRACK_1['spotify_track_uri']}>")
    
    def test_spotify_track_id(self):
        """Test for valid Spotify track_id"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.spotify_track_id, TEST_TRACK_1['spotify_track_id'])

    def test_name(self):
        """Test for valid track name"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.name, TEST_TRACK_1['name'])

    def test_spotify_track_uri(self):
        """Test for valid spotify_track_uri"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.spotify_track_uri, TEST_TRACK_1['spotify_track_uri'])

    def test_spotify_release_year(self):
        """Test for valid release_year"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.release_year, TEST_TRACK_1['release_year'])

    def test_popularity(self):
        """Test for valid popularity"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.popularity, TEST_TRACK_1['popularity'])

    def test_album_id(self):
        """Test for valid album_id"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.album_id, TEST_TRACK_1['album_id'])

    def test_acousticness(self):
        """Test for valid acousticness"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.acousticness, TEST_TRACK_1['acousticness'])

    def test_danceability(self):
        """Test for valid danceability"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.danceability, TEST_TRACK_1['danceability'])

    def test_energy(self):
        """Test for valid energy"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.energy, TEST_TRACK_1['energy'])

    def test_tempo(self):
        """Test for valid tempo"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.tempo, TEST_TRACK_1['tempo'])

    def test_instrumentalness(self):
        """Test for valid instrumentalness"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.instrumentalness, TEST_TRACK_1['instrumentalness'])

    def test_liveness(self):
        """Test for valid liveness"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.liveness, TEST_TRACK_1['liveness'])

    def test_loudness(self):
        """Test for valid loudness"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.loudness, TEST_TRACK_1['loudness'])

    def test_speechiness(self):
        """Test for valid speechiness"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.speechiness, TEST_TRACK_1['speechiness'])

    def test_valence(self):
        """Test for valid valence"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.valence, TEST_TRACK_1['valence'])

    def test_mode(self):
        """Test for valid mode"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.mode, TEST_TRACK_1['mode'])

    def test_key(self):
        """Test for valid key"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.key, TEST_TRACK_1['key'])

    def test_time_signature(self):
        """Test for valid time_signature"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.time_signature, TEST_TRACK_1['time_signature'])

    def test_lyrics(self):
        """Test for valid lyrics"""

        test_track = Track.query.get(self.track_id)

        self.assertEqual(test_track.lyrics, TEST_TRACK_1['lyrics'])