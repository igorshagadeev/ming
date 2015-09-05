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

import tempfile
import random
import os

from ming.ming import Ming
from settings import EXTENSIONS, UPLOAD_FOLDER



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

    return render_template('main.html', users = users, songs = songs, extensions = EXTENSIONS)



@app.route('/song/<song_id>')
def song(song_id):

    song = Song.query.filter(Song.id == song_id).one()
    #fingerprints = Fingerprint.query.all()

    return render_template('song.html', song = song)






ALLOWED_EXTENSIONS = set(EXTENSIONS)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS





@app.route('/upload', methods=['POST'])
def upload_file():
    """
    upload file to temporary, thend send to ming to process it
    and save features to database
    """
    f = request.files['file']
    if not (f and allowed_file(f.filename)):
        return redirect(url_for('hello'))

    if UPLOAD_FOLDER:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
    else:
        extension = secure_filename(f.filename).split('.')[-1]
        temp = tempfile.NamedTemporaryFile(suffix = '.'+extension)
        filepath = temp.name

    print filepath
    f.save(filepath)

    result = process_file(filepath)

    try:
        f.close()
        temp.close()
    except:
        print 'cant delete'

    return result



@app.route('/upload_search', methods=['POST'])
def upload_search():
    """
    upload file to temporary, thend send to ming to process it
    and compare to features in database

    return Counter object [(song1.id, N finds),(song2.id, M finds),]
    """
    f = request.files['file']
    if not (f and allowed_file(f.filename)):
        return redirect(url_for('hello'))
    
    if UPLOAD_FOLDER:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
    else:
        extension = secure_filename(f.filename).split('.')[-1]
        temp = tempfile.NamedTemporaryFile(suffix = '.'+extension)
        filepath = temp.name

    print filepath
    f.save(filepath)

    result = compare_file(filepath)

    try:
        f.close()
        temp.close()
    except:
        print 'cant delete'

    return result




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
