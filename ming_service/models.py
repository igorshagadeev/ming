from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship, backref

from database import db_session
#from sqlalchemy.orm.session import Session

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=False)
    email = Column(String(120), unique=False)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)






class Song(Base):
    __tablename__ = 'song'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    artist = Column(String(250), nullable=False)
    genres = Column(String(250), nullable=True)
    file_hash = Column(String(250), nullable=False)

    def __init__(self, title=None, artist=None, genres=None, file_hash=None):
        self.title = title
        self.artist = artist
        self.genres = genres
        self.file_hash = file_hash

    def __repr__(self):
        return '<Song %r>' % (self.title)

    def _count_fingerprints(self):
        return db_session.object_session(self).query(Fingerprint).with_parent(self).count()
    count_fingerprints = property(_count_fingerprints)


class Fingerprint(Base):
    __tablename__ = 'fingerprint'

    id = Column(Integer, primary_key=True)
    fp_hash = Column(String(250), nullable=False)

    song_id = Column(Integer, ForeignKey('song.id'))
    song = relationship("Song", backref=backref('fingerprints', order_by=id))

    def __init__(self, song=None, fp_hash=None):
        self.song = song
        self.fp_hash = fp_hash

    def __repr__(self):
        return '<FP for song %r>' % (self.song_id)






























