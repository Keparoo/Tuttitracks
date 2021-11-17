"""Authentication tools for Spotiflavor"""

import os
import base64
import requests
from flask import redirect, session, g
from models import User
from dotenv import load_dotenv
from app import CURR_USER_KEY

BASE_URL = 'https://api.spotify.com/v1'

load_dotenv()

# Spotify app client id and client secret
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

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
        Tokens are good for an hour. Set new token in session
        Return header with new bearer token
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
        session['auth'] = {
            "access_token": r.json()['access_token'],
            "token_type": r.json()['token_type'],
            "scope": r.json()['scope'],
            "expires_in": r.json()['expires_in']
            }

        new_bearer = r.json()['access_token']
        return {
            'Authorization': f'Bearer {new_bearer}'
        }


# class Spotify_Auth:
#     """Auth token class for Spotify"""

#     def __init__(self, access_token, token_type, scope, expires_in, refresh_token):
#         self.access_token = access_token
#         self.token_type = token_type
#         self.scope = scope
#         self.expires_in = expires_in
#         self.refresh_token = refresh_token
    
    
#     def __repr__(self):
#         """Return readable representation"""

#         return f'<Spotify_Auth {self.access_token} {self.scope} {self.expires_in} {self.refresh_token}>'