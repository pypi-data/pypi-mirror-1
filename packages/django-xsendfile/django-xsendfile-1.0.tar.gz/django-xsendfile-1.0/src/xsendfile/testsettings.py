import os, sys
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_ROOT, '..', '..', 'parts', 'static') 

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/notused.db'
INSTALLED_APPS = ['xsendfile']
ROOT_URLCONF = ['xsendfile.urls']

