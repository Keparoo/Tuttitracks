"""Tests for database api routes"""

from unittest import TestCase

from app import app, CURR_USER_KEY
from models import db, User, Track, Album, Artist, Playlist, Genre, PlaylistTrack, TrackArtist, TrackGenre
from flask import Flask, session, g
from sqlalchemy import exc
import requests

# Use test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spotiflavor_test'
app.config['SQLALCHEMY_ECHO'] = False

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# CURR_USER_KEY = 'curr_user'

BASE_URL = 'http://127.0.0.1:5000/api'

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

TEST_TRACK_2 = {
    "spotify_track_id": "testtrackid2",
    "name": "testname2",
    "spotify_track_uri": "testspotifytrackuri2",
    "release_year": 1990,

    "duration_ms": 2000,
    "album_id": 1,
    "popularity": 70,
    "acousticness": .7,
    "danceability": .7,
    "energy": .7,
    "tempo": 70.1,
    "instrumentalness": .7,
    "liveness": .7,
    "loudness": 0.7,
    "speechiness": .7,
    "valence": .7,
    "mode": 1,
    "key": 6,
    "time_signature": 6,
    "lyrics": "test lyrics 2"
}

TEST_TRACK_3 = {
    "spotify_track_id": "testtrackid3",
    "name": "testname3",
    "spotify_track_uri": "testspotifytrackuri3",
    "release_year": 1995,

    "duration_ms": 3000,
    "album_id": 1,
    "popularity": 90,
    "acousticness": .9,
    "danceability": .9,
    "energy": .9,
    "tempo": 90.1,
    "instrumentalness": .9,
    "liveness": .9,
    "loudness": 90.5,
    "speechiness": .9,
    "valence": .9,
    "mode": 0,
    "key": 9,
    "time_signature": 8,
    "lyrics": "test lyrics 3"
}

TEST_USER = {
    "username": "testuser",
    "password": "testpassword",
    "email": "testemail@test.com",
    "spotify_user_id": "TestSpotifyUid",
    "spotify_display_name": "TestUserDisplayName",
    "user_image": "http://www.test.com",
    "is_admin": True
}

TEST_PLAYLIST = {
    "username": TEST_USER['username'],
    "spotify_playlist_id": "testplaylistid",
    "spotify_snapshot_id": "testspotifysnapshotid",
    "image": "http://www.test@test.com",
    "public": True,
    "collaborative": False,
    "name": "testplaylistname",
    "description": "test description"
}

TEST_PLAYLIST_TRACK_1 = {
    "playlist_id": 1,
    "track_id": 1,
    "index": 1
}

TEST_PLAYLIST_TRACK_2 = {
    "playlist_id": 1,
    "track_id": 2,
    "index": 2
}

TEST_PLAYLIST_TRACK_3 = {
    "playlist_id": 1,
    "track_id": 3,
    "index": 3
}

class DB_API_TestCase(TestCase):
    """Tests for database API"""

    def setUp(self): 
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

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
        test_track_2 = Track(
            spotify_track_id=TEST_TRACK_2['spotify_track_id'],
            name=TEST_TRACK_2['name'],
            spotify_track_uri=TEST_TRACK_2['spotify_track_uri'],
            release_year=TEST_TRACK_2['release_year'],
            duration_ms=TEST_TRACK_2['duration_ms'],
            album_id=self.album_id,

            popularity=TEST_TRACK_2['popularity'],
            acousticness=TEST_TRACK_2['acousticness'],
            danceability=TEST_TRACK_2['danceability'],
            energy=TEST_TRACK_2['energy'],
            tempo=TEST_TRACK_2['tempo'],
            instrumentalness=TEST_TRACK_2['instrumentalness'],
            liveness=TEST_TRACK_2['liveness'],
            loudness=TEST_TRACK_2['loudness'],
            speechiness=TEST_TRACK_2['speechiness'],
            valence=TEST_TRACK_2['valence'],
            mode=TEST_TRACK_2['mode'],
            key=TEST_TRACK_2['key'],
            time_signature=TEST_TRACK_2['time_signature'],
            lyrics=TEST_TRACK_2['lyrics']
        )

        test_track_3 = Track(
            spotify_track_id=TEST_TRACK_3['spotify_track_id'],
            name=TEST_TRACK_3['name'],
            spotify_track_uri=TEST_TRACK_3['spotify_track_uri'],
            release_year=TEST_TRACK_3['release_year'],
            duration_ms=TEST_TRACK_3['duration_ms'],
            album_id=self.album_id,

            popularity=TEST_TRACK_3['popularity'],
            acousticness=TEST_TRACK_3['acousticness'],
            danceability=TEST_TRACK_3['danceability'],
            energy=TEST_TRACK_3['energy'],
            tempo=TEST_TRACK_3['tempo'],
            instrumentalness=TEST_TRACK_3['instrumentalness'],
            liveness=TEST_TRACK_3['liveness'],
            loudness=TEST_TRACK_3['loudness'],
            speechiness=TEST_TRACK_3['speechiness'],
            valence=TEST_TRACK_3['valence'],
            mode=TEST_TRACK_3['mode'],
            key=TEST_TRACK_3['key'],
            time_signature=TEST_TRACK_3['time_signature'],
            lyrics=TEST_TRACK_3['lyrics']
        )

        db.session.add(test_track_1)
        db.session.commit()
        db.session.add(test_track_2)
        db.session.commit()
        db.session.add(test_track_3)
        db.session.commit()
        self.track_1_id = 1
        self.track_2_id = 2
        self.track_3_id = 3

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

        test_user = User(
            username=TEST_USER['username'],
            password=TEST_USER['password'],
            email=TEST_USER['email'],
            spotify_user_id=TEST_USER['spotify_user_id'],
            spotify_display_name=TEST_USER['spotify_display_name'],
            user_image=TEST_USER['user_image'],
            is_admin=TEST_USER['is_admin']
        )

        db.session.add(test_user)
        db.session.commit()
        self.test_username = "testuser"
        self.test_user = test_user


        test_playlist = Playlist(
            username=TEST_PLAYLIST['username'],
            spotify_playlist_id=TEST_PLAYLIST['spotify_playlist_id'],
            spotify_snapshot_id=TEST_PLAYLIST['spotify_snapshot_id'],
            image=TEST_PLAYLIST['image'],
            public=TEST_PLAYLIST['public'],
            collaborative=TEST_PLAYLIST['collaborative'],
            name=TEST_PLAYLIST['name'],
            description=TEST_PLAYLIST['description']
        )

        db.session.add(test_playlist)
        db.session.commit()
        self.test_playlist_id = 1

        test_playlist_track_1 = PlaylistTrack(
            playlist_id=self.test_playlist_id,
            track_id=self.track_1_id,
            index=TEST_PLAYLIST_TRACK_1['index']
        )

        test_playlist_track_2 = PlaylistTrack(
            playlist_id=self.test_playlist_id,
            track_id=self.track_2_id,
            index=TEST_PLAYLIST_TRACK_2['index']
        )
        test_playlist_track_3 = PlaylistTrack(
            playlist_id=self.test_playlist_id,
            track_id=self.track_3_id,
            index=TEST_PLAYLIST_TRACK_3['index']
        )
        db.session.add(test_playlist_track_1)
        db.session.commit()
        db.session.add(test_playlist_track_2)
        db.session.commit()
        db.session.add(test_playlist_track_3)
        db.session.commit()
        self.test_playlist_track_1_id = 1
        self.test_playlist_track_2_id = 2
        self.test_playlist_track_3_id = 3

        
    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()

    #=======================================================================================
    # Datatbase API CRUD Tests    
    #=======================================================================================

    def test_create_playlist_route(self):
        """Test successful creation of a playlist"""

        self.assertEqual(1,1)

        payload = {
            "name": "New Test Playlist",
            "description":"New Test Description",
            "tracks": [1,2,3]
        }

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user

            res = requests.post(BASE_URL + f'/users/{self.test_username}/playlists', data=payload)

            self.assertEqual(res.status_code, 200)
            # self.assertTrue(res.json()['success'])
            # self.assertEqual(res.json()['name'], payload['name'])
            # self.assertEqual(res.json()['description'], payload['description'])
            # self.assertIsNotNone(res.json()['id'])
    
    def test_get_users_playlists(self):
        """Test successful get of users playlists"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_username
            res = requests.get(BASE_URL + f'/me/playlists')
        
            self.assertEqual(res.status_code, 200)