"""Authentication tools for Spotiflavor"""

import os
import base64
import requests
from functools import wraps
from flask import redirect, session, flash, abort, g
from models import User
from dotenv import load_dotenv

CURR_USER_KEY = 'curr_user'
BASE_URL = 'https://api.spotify.com/v1'

load_dotenv()

# Spotify app client id and client secret
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
# BASE_URL = 'https://api.spotify.com/v1'

REDIRECT_URI = os.environ.get('REDIRECT_URI')
SCOPE = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public user-top-read"

# Create headers for get_bearer_token and refresh_token
message = f"{CLIENT_ID}:{CLIENT_SECRET}"
messageBytes = message.encode('ascii')
base64Bytes = base64.b64encode(messageBytes)
base64Message = base64Bytes.decode('ascii')

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {base64Message}"
}

#====================================================================================
# Auth helpers
#====================================================================================

def get_spotify_user_code():
    """Get url containing spotify user coded needed to request bearer token"""

    r = requests.get(AUTH_URL, {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        "scope": SCOPE
    })

    return r.url

def get_user_id(token):
    """Query Spotify, and update user record with Spotify user id, Spotify display name, and Spotify user image"""

    headers = {
    'Authorization': f'Bearer {token}'
    }

    r = requests.get(BASE_URL + '/me', headers=headers)

    g.user.spotify_user_id = r.json()['id']
    g.user.spotify_display_name = r.json()['display_name']
    g.user.user_image = r.json()['images'][0]['url']
    User.update()
    

def get_bearer_token(code):
    """Get bearer token from Spotify"""

    data = {
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    try:
        r = requests.post(TOKEN_URL, headers=HEADERS, data=data)
    except:
        return {
            "error": "Authorization Error",
            "error_description": "Unable to get authorization token"
        }

    if r.status_code != 200:
        return {
            "error": r.status_code,
            "error_description": "Unable to get authorization token"
            }
    else:
        get_user_id(r.json()['access_token'])

        g.user.refresh_token = r.json()['refresh_token']
        User.update()
        return {
            "access_token": r.json()['access_token'],
            "token_type": r.json()['token_type'],
            "scope": r.json()['scope'],
            "expires_in": r.json()['expires_in'],
            "refresh_token": r.json()['refresh_token'],
            }

def refresh_token (refresh_token):
    """Request a refresh bearer token from Spotify
        Supply the original refresh token provided
        Perhaps this token should be stored in User
        Tokens are good for an hour. How to know when to refresh?
        Refactor this code and get_bearer_token to dry them up.
    
    """

    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    try:
        r = requests.post(TOKEN_URL, headers=HEADERS, data=data)
    except:
        return {
            "error": "Authorization Error",
            "error_description": "Unable to get authorization token"
        }

    if r.status_code != 200:
        return {
            "error": r.status_code,
            "error_description": "Unable to get authorization token"
            }
    else:
        return {
            "access_token": r.json()['access_token'],
            "token_type": r.json()['token_type'],
            "scope": r.json()['scope'],
            "expires_in": r.json()['expires_in'],
            "refresh_token": r.json()['refresh_token'],
            }

class Spotify_Auth:
    """Auth token class for Spotify"""

    def __init__(self, access_token, token_type, scope, expires_in, refresh_token):
        self.access_token = access_token
        self.token_type = token_type
        self.scope = scope
        self.expires_in = expires_in
        self.refresh_token = refresh_token
    
    def __repr__(self):
        """Return readable representation"""
        return f'<Spotify_Auth {self.access_token} {self.scope} {self.expires_in} {self.refresh_token}>'

#====================================================================================
# Auth decorators
#====================================================================================       

def requires_auth(username=''):
  '''Takes username from URL and checks if user is logged in'''

  def requires_auth_decorator(f):
      @wraps(f)
      def wrapper(username, *args, **kwargs):

        current_user = session.get(CURR_USER_KEY, None)

        if username != current_user.username:
            if current_user:
                flash('Access unauthorized', category='danger')
                # return redirect('/')
                abort(401)
            flash('Access unauthorized', category='danger')
            # return redirect('/')
            abort(401)
            
        return f(username, *args, **kwargs)

      return wrapper
  return requires_auth_decorator


# def requires_feedback_auth(feedback_id=None):
#   '''Takes feedback_id from URL and checks that it belongs to current logged in user'''

#   def requires_feedback_auth_decorator(f):
#       @wraps(f)
#       def wrapper(feedback_id, *args, **kwargs):
        
#         username = Feedback.query.get_or_404(feedback_id).user.username
#         current_user = session.get('username', None)

#         if username != current_user:
#             if current_user:
#                 flash('A user can only modify their own content!', category='danger')
#                 abort(401)
#             flash('You must be logged in to view or edit your feedback', category='danger')
#             abort(401)

#         return f(feedback_id, *args, **kwargs)

#       return wrapper
#   return requires_feedback_auth_decorator


def requires_signed_in(f):
    """Decorator restricting route to logged in users"""
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if CURR_USER_KEY not in session:
            flash('Access unauthorized', category='danger')
            # return redirect('/')
            abort(401)
        return f(*args, **kwargs)

    return decorated


def requires_signed_out(f):
    """Decorator restricting route to users not logged in"""
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' in session:
            flash('You are already logged in!', category='warning')
            user = session.get(CURR_USER_KEY)
            return redirect(f'/users/{user.username}')
        return f(*args, **kwargs)

    return decorated