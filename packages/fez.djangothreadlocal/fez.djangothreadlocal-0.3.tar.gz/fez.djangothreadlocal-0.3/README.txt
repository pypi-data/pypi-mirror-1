Introduction
============

Provides a simple middleware and API to get hold of the currently
logged-in user. 

Usage
=====

Simply add fez.djangothreadlocal.middleware.threadlocals.ThreadLocals
to your MIDDLEWARE_CLASSES in settings.py, for example:

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'fez.djangothreadlocal.middleware.threadlocals.ThreadLocals',
)

You should then be able to get hold of the current logged-in
user (or anonymous user) as follows:

from fez.djangothreadlocal.middleware import threadlocals
user = threadlocals.get_current_user()