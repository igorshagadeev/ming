# coding:utf-8

"""
web monitor and request module to sqlalchemy database with music files fingerprints

if database is empty go to module ming
and feed it with some directory with mp3 files
python ming.py -f /path/to/dir

author
Igor Shagadeev, shagastr@yandex.ru
"""

from flask import Flask, request
app = Flask(__name__)


from flask import Blueprint, current_app, render_template, url_for, redirect
from database import db_session, init_db, DB_URL
from werkzeug import secure_filename

#from sqlalchemy_utils.functions import database_exists
from tools import database_exists

from models import User, Song, Fingerprint

import random
import os

from ming.ming import Ming



#TODO
# import setting to project



#blueprint = Blueprint(
    #'',
    #__name__,
    #template_folder='templates',
    #static_folder='static',
#)

#@blueprint.route('/')

@app.route('/')
def hello():

    users = User.query.all()
    songs = Song.query.all()

    return render_template('main.html', users = users, songs = songs)



@app.route('/song/<song_id>')
def song(song_id):

    song = Song.query.filter(Song.id == song_id).one()
    #fingerprints = Fingerprint.query.all()

    return render_template('song.html', song = song)





UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['mp3'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def upload_file():

    f = request.files['file']

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
    print filepath
    f.save(filepath)

    result = process_file(filepath)

    return result



@app.route('/upload_search', methods=['POST'])
def upload_search():

    f = request.files['file']

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
    print filepath
    f.save(filepath)

    result = compare_file(filepath)

    return result




#TODO
################################
#
#   flask views grab form db module
#        - grab list of songs
#
################################
#
#   views send to processing service
#       process_file - send file to processing
#
################################



#TODO
# write def to processing service
# deal with uploaded file
def process_file(filepath):

    m = Ming()
    m.fingerprint_file(filepath)

    return redirect(url_for('hello'))




def compare_file(filepath):

    m = Ming()
    song, results = m.compare_file(filepath )

    song_results = []
    for k, v in results:
        song_results.append((Song.query.filter(Song.id == k).one() , v))

    return render_template('comparison.html', song = song, results = song_results)






@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()





@app.route('/add_user')
def add_user():

    letters = 'qwertyuiopasdfghjklzxcvbnm'

    def rand_name(i = 6):
        name = ''
        for i in range(i):
            name+=letters[random.randint(0,len(letters)-1)]
        return name

    name = rand_name(random.randint(3,10))

    u = User(name, name+'@localhost')
    db_session.add(u)
    db_session.commit()

    return redirect(url_for('hello'))






#@app.cli.command()
def initdb():
    """Initialize the database."""

    # try connect to db
    # show its structure

    #else
    init_db()

    print '-'*10
    print 'Initializing db at '+ DB_URL

    return







if __name__ == '__main__':

    if not database_exists(DB_URL):
        initdb()

    app.run(debug=True)
