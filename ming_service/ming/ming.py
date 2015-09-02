# coding:utf-8

"""
main module - processing service

extract features from music file 
fingerprints,

#Perceptual characteristics often exploited by audio fingerprints include
# average zero crossing rate,
# estimated tempo,
# average spectrum,
# spectral flatness,
# prominent tones across a set of bands,
# bandwidth.

author
Igor Shagadeev, shagastr@yandex.ru
"""


import os, sys
parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(parent_dir)


import fingerprint as fp

import eyed3

from abc import ABCMeta, abstractmethod


from tools import database_exists
from models import Song, Fingerprint
from database import db_session, init_db, DB_URL
from ingest.ingestion import grab_files

from hashlib import sha1

import argparse




class fileformatHandler(object):
    """
    interface for 'file format' ->  wav decoders
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def decode_to_wav(self, filename):
        """
        decode this file format to wav
        """
        pass



class mp3Handler(fileformatHandler):
    def decode_to_wav(self, filename):
        """
        decode this mp3 format to wav with linux mpg123 codec command
        #mpg123 --wav test.wav --8bit --rate 8000 --mono test.mp3
        """
        import tempfile
        import commands
        import os
        from scipy.io.wavfile import read

        temp = tempfile.NamedTemporaryFile()
        try:
            print 'temp:', temp
            print 'temp.name:', temp.name

            os.system("mpg123 --wav " + temp.name + " --8bit --rate 8000 --mono " + filename)

            #convert to array
            rate, data = read(temp.name)

        finally:
            # Automatically cleans up the file
            temp.close()


        return rate, data




HANDLERS = {'mp3':mp3Handler,}



class formatHandlerFactory(object):
    """
    factory object to use appropriate handler
    """
    @staticmethod
    def get_handler(filetype):
        try:
            obj = HANDLERS[filetype]()
        except KeyError:
            return None

        return obj



















class Ming(object):
    """

    Interface to music file processing

    initialize all components
    ping or init:

    1 ingest service
    2 database - fp storage
    3 distributed task handler
    4 reporting module

    1 retrieve files from data storages
    2 make jobs
    3 run jobs on machines, using maximum cpus
    4 get completed tasks
    5 write fp's to database

    get some files and make jobs
    """
    def __init__(self):

        #check if db exists
        if not database_exists(DB_URL):
            print '-'*10
            print 'Initializing db at '+ DB_URL
            init_db()
            print 'successfull'
            print '-'*10

        self.db_session = db_session

        super(Ming, self).__init__()


    def extract_tags(self, filepath):
        """
        extract tags from file
        """
        import eyed3


        audiofile = eyed3.load(filepath)

        artist = audiofile.tag.artist
        title = audiofile.tag.title
        genre = audiofile.tag.genre

        if genre:
            genre_name = genre.name
        else:
            genre_name = None

        return (artist, title, genre_name)

    def get_text(self, artist, title):
        """
        try to get song text from 3d party source
        """
        text = ''

        return text


    def text_slogan(self, text):
        """
        extract main idea of text
        """

        pass

    def text_sentiment(self, text):
        """
        estimate list of sentiment genres of text
        """

        pass

    def save_song(self, title, artist, genres, file_hash):

        song = Song(title, artist, genres, file_hash)
        self.db_session.add(song)
        self.db_session.commit()

        return song


    def save_hashes(self, song, hashes):
        """
        save song model to database
        """
        for h in hashes:
            fingerprint = Fingerprint(song=song, fp_hash=h)
            self.db_session.add(fingerprint)
        self.db_session.commit()

        return True

    def fingerprint_file(self, filepath):
        """
        process file to fingerprints and store them in database
        """

        # check file format and use appropriate handler
        file_format = filepath.split('.')[-1]
        handler = formatHandlerFactory.get_handler(file_format)

        # get file_hash to not process the same file
        file_hash = unique_hash(filepath)
        exists = self.db_session.query(Song).filter(Song.file_hash == file_hash).first()
        print 'exists', exists

        if exists:
            print 'file %s already processed in db' % filepath
            return None

        # get tags
        artist, title, genres = self.extract_tags(filepath)
        print 'tags:', artist, title, genres

        ### make fp
        # prepare wav
        rate, data = handler.decode_to_wav(filepath)

        #process data
        hashes = fp.process_file(rate, data, filepath, vizualize=False)


        # db.insert_song
        song = self.save_song(title, artist, genres, file_hash)

        # db.insert_hashes
        self.save_hashes(song, hashes)

        return None


    def fingerprint_dir(self, dirpath):
        """
        process all files to fingerprints and store them in database
        """
        # 
        for file_path in grab_files(dirpath, extensions = ('.mp3',)):
            print file_path
            self.fingerprint_file(file_path)

    def compare_file(self, filepath, max_common=10):
        """
        process file to fingerprints and search in database
        similar, setting treshold to 1% ?
        """

        # check file format and use appropriate handler
        file_format = filepath.split('.')[-1]
        handler = formatHandlerFactory.get_handler(file_format)

        # get tags
        artist, title, genre = self.extract_tags(filepath)
        print 'tags:', artist, title, genre

        ### make fp
        # prepare wav
        rate, data = handler.decode_to_wav(filepath)

        #process data
        hashes = fp.process_file(rate, data, filepath, vizualize=False)

        similarity_dict = {}
        similarity_list = []
        for h in hashes:
            found = self.db_session.query(Fingerprint).filter(Fingerprint.fp_hash == h)

            #similarity_dict.update
            similarity_list += [h.song_id for h in found]

        from collections import Counter
        results = Counter(similarity_list).most_common(max_common)

        file_hash = unique_hash(filepath)

        song = Song(title, artist, file_hash)

        print results
        return (song, results)














def unique_hash(filepath, blocksize=2**20):
    """ Small function to generate a hash to uniquely generate
    a file. Inspired by MD5 version here:
    http://stackoverflow.com/a/1131255/712997

    Works with large files. 
    """
    s = sha1()
    with open(filepath, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            s.update(buf)
    return s.hexdigest().upper()





if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Ming music fingerprint",
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-f', '--fingerprint', nargs=1,
                        help='Fingerprint file\n'
                             'Usage: \n'
                             '--fingerprint /path/to/directory/file.mp3')

    parser.add_argument('-r', '--recognize', nargs=1,
                        help='Recognize what is '
                             'file similar to\n'
                             'Usage: \n'
                             '--recognize file path/to/file \n')

    args = parser.parse_args()

    if not args.fingerprint and not args.recognize:
        parser.print_help()
        sys.exit(0)

    if args.fingerprint:
        # Fingerprint file and store to database

        if len(args.fingerprint) == 1:
            filepath = args.fingerprint[0]
            if os.path.isfile(filepath):
                m = Ming()
                m.fingerprint_file(filepath)

            elif os.path.isdir(filepath):
                m = Ming()
                m.fingerprint_dir(filepath)

    elif args.recognize:
        # Recognize audio file
        filepath = args.recognize[0]

        m = Ming()
        song, results = m.compare_file(filepath)

        song_results = []
        for k, v in results:
            song_results.append((m.db_session.query(Song).filter(Song.id == k).one() , v))

        print song_results

    sys.exit(0)

    # manual test
    #filename = '/home/shandec/ming/fixtures/splin_-_mamma_mia.mp3'
    #m = Ming()
    #m.fingerprint_file(filename)






















































