"""Tests for Playlist and PlaylistTrack models"""

from unittest import TestCase

from app import app
from models import db, User, Track, Album, Playlist, PlaylistTrack
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
        db.session.add(test_playlist_track_1)
        db.session.commit()
        db.session.add(test_playlist_track_2)
        db.session.commit()
        self.test_playlist_track_1_id = 1
        self.test_playlist_track_2_id = 2

        
    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()

    #=======================================================================================
    # Playlist Model Tests    
    #=======================================================================================

    def test_playlist_repr_(self):

        test_playlist = Playlist.query.get(self.test_playlist_id)

        self.assertEqual(Playlist.__repr__(test_playlist), f"<Playlist {self.test_playlist_id} {TEST_PLAYLIST['username']} {TEST_PLAYLIST['name']} {TEST_PLAYLIST['description']} {TEST_PLAYLIST['spotify_playlist_id']} {TEST_PLAYLIST['spotify_snapshot_id']}>")

    def test_username(self):
        """Test for valid username"""

        test_playlist = Playlist.query.get(self.test_playlist_id)

        self.assertEqual(test_playlist.username, TEST_PLAYLIST['username'])

    def test_spotify_playlist_id(self):
        """Test for valid spotify_playlist_id"""

        test_playlist = Playlist.query.get(self.test_playlist_id)

        self.assertEqual(test_playlist.spotify_playlist_id, TEST_PLAYLIST['spotify_playlist_id'])

    def test_spotify_spotify_snapshot_id(self):
        """Test for valid spotify_snapshot_id"""

        test_playlist = Playlist.query.get(self.test_playlist_id)

        self.assertEqual(test_playlist.spotify_snapshot_id, TEST_PLAYLIST['spotify_snapshot_id'])

    def test_image(self):
        """Test for valid image"""

        test_playlist = Playlist.query.get(self.test_playlist_id)

        self.assertEqual(test_playlist.image, TEST_PLAYLIST['image'])

    def test_public(self):
        """Test for valid public"""

        test_playlist = Playlist.query.get(self.test_playlist_id)

        self.assertEqual(test_playlist.public, TEST_PLAYLIST['public'])

    def test_collaborative(self):
        """Test for valid collaborative"""

        test_playlist = Playlist.query.get(self.test_playlist_id)

        self.assertEqual(test_playlist.collaborative, TEST_PLAYLIST['collaborative'])

    def test_name(self):
        """Test for valid name"""

        test_playlist = Playlist.query.get(self.test_playlist_id)

        self.assertEqual(test_playlist.name, TEST_PLAYLIST['name'])

    def test_description(self):
        """Test for valid name"""

        test_playlist = Playlist.query.get(self.test_playlist_id)

        self.assertEqual(test_playlist.description, TEST_PLAYLIST['description'])

    def test_playlists_tracks_repr(self):
        """Test success of repr for playlists_tracks"""

        test_playlists_tracks = PlaylistTrack.query.get(self.test_playlist_track_1_id)

        self.assertEqual(PlaylistTrack.__repr__(test_playlists_tracks), f"<PlaylistTrack {self.test_playlist_track_1_id} {TEST_PLAYLIST_TRACK_1['playlist_id']} {TEST_PLAYLIST_TRACK_1['track_id']} {TEST_PLAYLIST_TRACK_1['index']}>")      

    def test_playlist_to_tracks(self):
        """Test for valid connection from playlists to tracks"""

        test_playlist = Playlist.query.get(self.test_playlist_id)
        track_1 = test_playlist.tracks[0]
        track_2 = test_playlist.tracks[1]

        self.assertEqual(track_1.id, self.track_1_id)
        self.assertEqual(track_2.id, self.track_2_id)

    def test_tracks_to_playlists(self):
        """Test for valid connection from tracks to playlists"""

        test_track = Track.query.get(self.track_1_id)
        playlist = test_track.playlist[0]

        self.assertEqual(playlist.id, self.test_playlist_id)

    def test_playlists_to_user(self):
        """Test for valid connection from playlists to user"""

        test_playlist = Playlist.query.get(self.test_playlist_id)
        user = test_playlist.user

        self.assertEqual(user.username, TEST_USER['username'])
 