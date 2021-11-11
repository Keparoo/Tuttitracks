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
    "is_admin": "True"
}

class UserModelTestCase(TestCase):
    """Tests for user model"""

    def setUp(self): 
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.register(**TEST_USER_1)
        self.username1 = "testuser1"

        db.session.add(u1)
        db.session.commit()

        self.u1 = User.query.get(self.username1)
        
    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()

    #=========================================================================================================
    # Create User Model Tests    
    #=========================================================================================================

    def test_register(self):
        """Test successful user registration"""

        user = User.register("usersignuptest", "password", "signup@signup.com", "US")
        username = "usersignuptest"
        db.session.add(user)
        db.session.commit()

        user = User.query.get(username)
        self.assertEqual(user.username, "usersignuptest")
        self.assertEqual(user.email, "signup@signup.com")
        self.assertEqual(user.country, "US")
        self.assertIsNotNone(user.password)

        self.assertEqual(User.__repr__(user), f"<User {self.username} {self.email} {self.country} {self.spotify_user_id} {self.spotify_display_name} {self.is_admin}>")