import os

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_DIRS = (
    'templates'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'core.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'changeset',
    'core'
)

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = None
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
DEBUG = False
USE_I18N = True
SITE_ID = 1

ADMIN_MEDIA_PREFIX = '/admin/media/'

MEDIA_SERVE = True
MEDIA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'core', 'media'))
MEDIA_URL = '/media'

SECRET_KEY = None

TEMPLATE_DIRS = []

ALLOW_ANONYMOUS = True
ALLOW_REGISTRATION = True

SQUASH_HOME = os.path.abspath(os.path.dirname(__file__))

USER = os.environ['USER']

### Setting Overrides ###
import yaml

for path in ('.squash', os.path.expanduser(os.environ.get('SQUASH_HOME', '')), os.path.expanduser('~/.squash')):
    if os.path.exists(path):
        if os.path.exists(os.path.join(path, 'settings.py')):
            execfile(os.path.join(path, 'settings.py'), globals())
            globals()['SQUASH_HOME'] = os.path.abspath( path )
            break
        
        yaml = os.path.join(path, 'settings.yaml')
        if os.path.exists(yaml):
            for k, v in yaml.load( open(yaml) ).items():
                globals()[k.upper()] = v
            globals()['SQUASH_HOME'] = os.path.abspath( path )
            break

if not DATABASE_NAME and DATABASE_ENGINE == 'sqlite3':
    DATABASE_NAME = os.path.abspath( os.path.join(SQUASH_HOME, 'sqlite3.db') )

try:
    from settings_local import *
except ImportError:
    pass