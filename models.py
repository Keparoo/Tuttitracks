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
    """Model for a User class"""

    __tablename__ = 'users'

    username = db.Column(db.String(25), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
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