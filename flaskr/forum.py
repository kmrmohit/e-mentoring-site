from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('forum', __name__,url_prefix='/dashboard')

@bp.route('/')
@login_required
def dashboard():
    return render_template('forum/dashboard.html')


@bp.route('/ask', methods=('GET', 'POST'))
@login_required
def ask():
    if request.method == 'POST':
        title = request.form['title']
        print(title)
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO questions (author_id,body)'
                ' VALUES (?, ?)',
                (g.user['id'],title)
            )
            db.commit()
            print("data added")
            return redirect(url_for('forum.dashboard'))

    return render_template('forum/ask.html')


@bp.route('/<int:id>/profile', methods=('GET', 'POST'))
@login_required
def view_profile(id):
    return render_template('auth/profile.html')

@login_required
def view_ques():
    db = get_db()
    ques = db.execute(
            'SELECT DISTINCT q.id as qid, body as qbody,created'
            ' FROM questions q '
            ' WHERE q.author_id != ?'
            ' ORDER BY qid DESC',
            ( g.user['id'] ,)
        ).fetchall()
    try:
        return render_template('forum/other_ques.html',posts=ques)
    except:
        print("no questions yet")

@bp.route('/answer', methods=('GET', 'POST'))
@login_required
def view_ques():
    db = get_db()
    ques = db.execute(
            'SELECT DISTINCT q.id as qid, body as qbody,created'
            ' FROM questions q '
            ' WHERE q.author_id != ?'
            ' ORDER BY qid DESC',
            ( g.user['id'] ,)
        ).fetchall()
    try:
        return render_template('forum/other_ques.html',posts=ques)
    except:
        print("no questions yet")

def get_ques(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id,p.body,author_id'
        ' FROM questions p'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))



    return post

@bp.route('/<int:id>/your_ques', methods=('GET', 'POST'))
@login_required
def your_ques(id):
    db = get_db()
    ques = db.execute(
            ' SELECT DISTINCT q.id as qid, body as qbody ,created'
            ' FROM questions q , user u '
            ' WHERE q.author_id = ? '
            ' ORDER BY qid DESC ',
            ( id ,)
        ).fetchall()
        #print("hi")
    return render_template('forum/your_ques.html', posts=ques)



@bp.route('/<int:id>/answer', methods=('GET', 'POST'))
@login_required
def answer(id):
    ques = get_ques(id)
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Body is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO answers (question_id,body)'
                ' VALUES (?, ?)',
                (id,body)
            )
            db.commit()
            det=db.execute(
              'SELECT *'
              'FROM answers'
            ).fetchall()
            for items in det:
                print(items['body'])
            return redirect(url_for('forum.dashboard'))

    return render_template('forum/answer.html', posts=ques)


@bp.route('/<int:uid>/view_answers', methods=('GET', 'POST'))
@login_required
def view_answers(uid):
    db = get_db()
    error = None
    res = db.execute(
            ' SELECT DISTINCT question_id, id , body ,created'
            ' FROM answers a '
            ' WHERE a.question_id = ? ',
            (uid,)
    ).fetchall()
    if(len(res)==0):
        error="No answers for this question yet."
    if error is not None:
        flash(error)
#    print(len(res))
#    for items in res:
#        print(str(items["question_id"]) + " " +str(items["id"]) + " " + items["body"])

    return render_template('forum/view_answers.html', posts=res)
