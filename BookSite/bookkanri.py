from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from BookSite.auth import login_required
from BookSite.db import get_db

bp = Blueprint('bookKanri', __name__)


@bp.route('/')
def index():
    """Show all the bookDatas, most recent first."""
    db = get_db()
    bookDatas = db.execute(
        'SELECT p.id, bookTitle, author, publisher, price, purchaseDate, memo,  manager_id, managername, created'
        ' FROM bookData p JOIN manager u ON p.manager_id = u.id'
        ' ORDER BY bookTitle'
    ).fetchall()
    return render_template('bookKanri/index.html', bookDatas=bookDatas)


def get_bookData(id, check_author=True):
    """Get a bookDataand its author by id.
    Checks that the id exists and optionally that the current manager is
    the author.
    :param id: id of bookDatato get
    :param check_author: require the current manager to be the author
    :return: the bookDatawith author information
    :raise 404: if a bookDatawith the given id doesn't exist
    :raise 403: if the current manager isn't the author
    """
    bookData= get_db().execute(
        'SELECT p.id, bookTitle, author, publisher, price, purchaseDate, memo,  manager_id, managername'
        ' FROM bookData p JOIN manager u ON p.manager_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if bookData is None:
        abort(404, "bookData id {0} doesn't exist.".format(id))

    if check_author and bookData['manager_id'] != g.manager['id']:
        abort(403)

    return bookData


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new bookDatafor the current manager."""
    if request.method == 'POST':
        bookTitle = request.form['bookTitle']
        author = request.form['author']
        publisher = request.form['publisher']
        price = request.form['price']
        purchaseDate = request.form['purchaseDate']
        memo = request.form['memo']
        error = None

        if not bookTitle:
            error = 'bookTitle is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO bookData(bookTitle, author, publisher, price, purchaseDate, memo, manager_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (bookTitle, author, publisher, price, purchaseDate, memo, g.manager['id'])
            )
            db.commit()
            return redirect(url_for('bookKanri.index'))

    return render_template('bookKanri/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a bookDataif the current manager is the author."""
    bookData= get_bookData(id)

    if request.method == 'POST':
        bookTitle = request.form['bookTitle']
        author = request.form['author']
        publisher = request.form['publisher']
        price = request.form['price']
        purchaseDate = request.form['purchaseDate']
        memo = request.form['memo']
        error = None

        if not bookTitle:
            error = 'bookTitle is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE bookData SET bookTitle = ?, author = ?,  publisher = ?, price = ?, purchaseDate = ?, memo = ? WHERE id = ?',
                (bookTitle, author, publisher, price, purchaseDate, memo, id)
            )
            db.commit()
            return redirect(url_for('bookKanri.index'))

    return render_template('bookKanri/update.html', bookData=bookData)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete a bookData.
    Ensures that the bookDataexists and that the logged in manager is the
    author of the bookData.
    """
    get_bookData(id)
    db = get_db()
    db.execute('DELETE FROM bookData WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('bookKanri.index'))
