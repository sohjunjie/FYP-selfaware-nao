import os


try:
    os.remove('database/database.sqlite')
except OSError:
    pass


from database.definition import *
from pony.orm import *
populate_database()
