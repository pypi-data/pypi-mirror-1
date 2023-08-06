import os

SITE_ID = 1

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/links.db'
INSTALLED_APPS = ['django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'emencia.django.links',]
ROOT_URLCONF = 'emencia.django.links.urls'

LANGUAGE_CODE = 'en'

LANGUAGES = (('fr', 'French'),
             ('en', 'English'),
             )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',)
