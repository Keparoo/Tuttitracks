"""Spotiflavor Springboard Capstone 1"""

import os
from flask import Flask, render_template, request, redirect, flash, session
from dotenv import load_dotenv

from models import db, connect_db, User
from forms import LoginUserForm, RegisterUserForm
from auth import requires_signed_in, requires_auth, requires_feedback_auth, requires_signed_out

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['DEBUG'] = False

connect_db(app)
db.create_all()

@app.route('/')
def homepage():
    """Display homepage"""



#====================================================================================
# error handlers
#====================================================================================

@app.errorhandler(404)
def resource_not_found(error):
    return render_template('/errors/404.html'), 404

@app.errorhandler(401)
def resource_not_found(error):
    return render_template('/errors/401.html'), 401

@app.errorhandler(403)
def resource_not_found(error):
    return render_template('/errors/403.html'), 403

@app.errorhandler(500)
def resource_not_found(error):
    return render_template('/errors/500.html'), 500