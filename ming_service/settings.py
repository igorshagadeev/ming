# coding:utf-8



###############################################################################
#                           GLOBAL SECTION



# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# extensions list to analyse
# check that holder for each extension defined (test)
# flask use this to filter uploaded files
EXTENSIONS = ['.mp3',]

# upload dir for flask service
# if None uses NamedTemporary file by default with .mp3 extension
# if specified - will store to disk
UPLOAD_FOLDER = None

# Application threads.
THREADS_NUMBER = 2

# Secret key
SECRET_KEY = "secret"




###############################################################################
#                           DATABASE SECTION



# Define the database - we are working with
# SQLite for this example
#DB_URL = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
DB_URL = 'sqlite:////tmp/test.db'

# default postgresql
#DB_URL = 'postgresql://scott:tiger@localhost/mydatabase'

# psycopg2
#DB_URL = 'postgresql+psycopg2://scott:tiger@localhost/mydatabase'










































