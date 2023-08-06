import os
 
DEBUG = TEMPLATE_DEBUG = True
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'encrypt.db'
INSTALLED_APPS = (
    'encrypt',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
)
ROOT_URLCONF = ['encrypt.urls']

TEMPLATE_DIRS = os.path.join(os.path.dirname(__file__), 'templates')

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
