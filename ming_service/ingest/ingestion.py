#coding: utf-8

"""
ingestion module
"""

import os
from settings import EXTENSIONS

def grab_files(dirpath, extensions=None):
    """
    generator returning all files in dir with certain extensions e.g. ('.mp3',)
    """
    if not extensions:
        extensions = EXTENSIONS
        print 'looking for ', extensions, ' extensions in ', dirpath

    for name in os.listdir(dirpath):
        full_path = os.path.join(dirpath, name)
        if os.path.isdir(full_path):
            for entry in grab_files(full_path):
                yield entry
        elif os.path.isfile(full_path):
            if full_path.endswith(extensions):
                yield full_path




if __name__ == '__main__':

    dirpath = '/tmp/'
    for f in grab_files(dirpath):
        print f






























