"""Tests for user model and authentication"""

from unittest import TestCase

from app import app
from models import db, User
from flask import Flask, session
from sqlalchemy import exc

# Use test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spotiflavor_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

TEST_USER_1 = {
    "username": "testuser1",
    "password": "testpassword1",
    "email": "testemail1@test.com",
    "spotify_user_id": "TestSpotifyUid",
    "spotify_display_name": "TestUserDisplayName",
    "user_image": "http://www.test.com",
    "is_admin": True
}

U1 = {
    "username": "testuser1",
    "password": "testpassword1",
    "email": "testemail1@test.com",
    "user_image": "http://www.test.com"
}


class UserModelTestCase(TestCase):
    """Tests for user model"""

    def setUp(self): 
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        testuser = User(
            username="testuser",
            password="testpassword",
            email="testemail@test.com",
            spotify_user_id="TestSpotifyUid",
            spotify_display_name="TestUserDisplayName",
            user_image="http://www.test.com",
            is_admin=True
        )
        db.session.add(testuser)
        db.session.commit()
        self.testusername = "testuser"

        u1 = User.signup(**U1)
        self.username1 = "testuser1"
        db.session.add(u1)
        db.session.commit()
        self.u1 = User.query.get(self.username1)

        
    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()

    #=======================================================================================
    # User Model Tests    
    #=======================================================================================

    def test_signup(self):
        """Test successful user registration"""

        user = User.signup("usersignuptest", "password", "signup@signup.com", "http://www.test.com")
        username = "usersignuptest"
        db.session.add(user)
        db.session.commit()

        user = User.query.get(username)
        self.assertEqual(user.username, "usersignuptest")
        self.assertEqual(user.email, "signup@signup.com")
        self.assertIsNotNone(user.password)

        self.assertEqual(User.__repr__(user), f"<User {user.username} {user.email} {user.spotify_user_id} {user.spotify_display_name} {user.is_admin}>")

    def test_invalid_username_signup(self):
        """Test invalid empty username signup"""

        empty_username_user = User.signup(None, "password", "signup@signup.com", "http://www.test.com")
        db.session.add(empty_username_user)

        # sqlalchemy will raise error as nullable=False
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        """Test invalid empty email signup"""

        empty_email_user = User.signup("usersignuptest", "password", None, "http://www.test.com")
        db.session.add(empty_email_user)

        # sqlalchemy will raise error as nullable=False
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """Test invalid empty or null-string password signup"""

        with self.assertRaises(ValueError) as context:
            User.signup("usersignuptest", None, "signup@signup.com", "http://www.test.com")

        with self.assertRaises(ValueError) as context:
            User.signup("usersignuptest", "", "signup@signup.com", "http://www.test.com")

    def test_spotify_user_id(self):
        """Test for valid Spotify user id"""

        testuser = User.query.get(self.testusername)

        self.assertEqual(testuser.spotify_user_id, "TestSpotifyUid")

    def test_spotify_display_name(self):
        """Test for valid Spotify display name"""

        testuser = User.query.get(self.testusername)

        self.assertEqual(testuser.spotify_display_name, "TestUserDisplayName")

    def test_spotify_is_admin(self):
        """Test for valid Spotify display name"""

        testuser = User.query.get(self.testusername)

        self.assertEqual(testuser.is_admin, True)


    #=======================================================================================
    # Authentication Tests    
    #=======================================================================================

    def test_authenticate(self):
        """Test authentication of user"""

        user = User.authenticate(self.u1.username, "testpassword1")
        self.assertIsNotNone(user)
        self.assertEqual(self.u1.username, self.u1.username)

    def test_invalid_username(self):
        """Test invalid username"""

        self.assertFalse(User.authenticate("wrongusername", "testpassword1"))

    def test_invalid_password(self):
        """Test invalid password"""

        self.assertFalse(User.authenticate(self.u1.username, "wrongpassword"))