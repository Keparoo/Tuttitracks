"""Authentication tools for Spotiflavor"""

from functools import wraps
from flask import redirect, session, flash, abort
from models import User


def requires_auth(username=''):
  '''Takes username from URL and checks if user is logged in'''

  def requires_auth_decorator(f):
      @wraps(f)
      def wrapper(username, *args, **kwargs):

        current_user = session.get('username', None)

        if username != current_user:
            if current_user:
                flash('A user can only modify their own content!', category='danger')
                abort(401)
            flash('You must be logged in to view or edit your info', category='danger')
            abort(401)
            
        return f(username, *args, **kwargs)

      return wrapper
  return requires_auth_decorator


def requires_feedback_auth(feedback_id=None):
  '''Takes feedback_id from URL and checks that it belongs to current logged in user'''

  def requires_feedback_auth_decorator(f):
      @wraps(f)
      def wrapper(feedback_id, *args, **kwargs):
        
        username = Feedback.query.get_or_404(feedback_id).user.username
        current_user = session.get('username', None)

        if username != current_user:
            if current_user:
                flash('A user can only modify their own content!', category='danger')
                abort(401)
            flash('You must be logged in to view or edit your feedback', category='danger')
            abort(401)

        return f(feedback_id, *args, **kwargs)

      return wrapper
  return requires_feedback_auth_decorator


def requires_signed_in(f):
    """Decorator restricting route to logged in users"""
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash('You must be logged in to view!', category='danger')
            abort(401)
        return f(*args, **kwargs)

    return decorated


def requires_signed_out(f):
    """Decorator restricting route to users not logged in"""
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' in session:
            flash('You are already logged in!', category='warning')
            username = session.get('username')
            return redirect(f'/users/{username}')
        return f(*args, **kwargs)

    return decorated