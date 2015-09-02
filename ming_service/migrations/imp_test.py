

import os, sys
#sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

#print os.getcwd()

parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(parent_dir)


print sys.path

#from ming_service import database
#import database
from database import Base

print Base
#print database.Base