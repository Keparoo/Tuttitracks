from app import app
from models import db, User


db.drop_all()
db.create_all()

user1 = User(
    username="bob",
    password="$2b$12$U3DOsRsgBxZ3VXcWoflq3eN7Z1TEs5VqVC.tHRh6z.CoxOZpN5Fmu",
    email="bob@bob.com",
    spotify_user_id="",
    spotify_display_name="",
    user_image="",
    country="US",
    refresh_token="",
    is_admin=True
)

user2 = User(
    username="ben",
    password="$2b$12$ek..ijP4Pd9rZH5HLG9IWeVM5RycH45BwXJbqhq7klBT0G/ebKzoe",
    email="ben@ben.com",
    spotify_user_id="",
    spotify_display_name="",
    user_image="",
    country="FR",
    refresh_token="",
    is_admin=False
)

db.session.add_all([user1, user2])
db.session.commit()