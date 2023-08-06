import os

curdir = os.path.dirname(__file__)
curdir = os.path.realpath(curdir)

DB_FILE = os.path.join(curdir, 'xapian.database')
SQLURI = 'sqlite:///afpy.xap.db'

