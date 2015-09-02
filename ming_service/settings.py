# coding:utf-8



# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

DB_URL = 'sqlite:////tmp/test.db'
DATABASE_CONNECT_OPTIONS = {}




# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_NUMBER = 2





# Secret key
SECRET_KEY = "secret"



































