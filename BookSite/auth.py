import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from BookSite.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator that redirects anonymous managers to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.manager is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_manager():
    """If a manager id is stored in the session, load the manager object from
    the database into ``g.manager``."""
    manager_id = session.get('manager_id')

    if manager_id is None:
        g.manager = None
    else:
        g.manager = get_db().execute(
            'SELECT * FROM manager WHERE id = ?', (manager_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new manager.
    Validates that the managername is not already taken. Hashes the
    password for security.
    """
    if request.method == 'POST':
        managername = request.form['managername']
        password = request.form['password']
        db = get_db()
        error = None

        if not managername:
            error = 'managername is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM manager WHERE managername = ?', (managername,)
        ).fetchone() is not None:
            error = 'manager {0} is already registered.'.format(managername)

        if error is None:
            # the name is available, store it in the database and go to
            # the login page
            db.execute(
                'INSERT INTO manager (managername, password) VALUES (?, ?)',
                (managername, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered manager by adding the manager id to the session."""
    if request.method == 'POST':
        managername = request.form['managername']
        password = request.form['password']
        db = get_db()
        error = None
        manager = db.execute(
            'SELECT * FROM manager WHERE managername = ?', (managername,)
        ).fetchone()

        if manager is None:
            error = 'Incorrect managername.'
        elif not check_password_hash(manager['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # store the manager id in a new session and return to the index
            session.clear()
            session['manager_id'] = manager['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """Clear the current session, including the stored manager id."""
    session.clear()
    return redirect(url_for('index'))
