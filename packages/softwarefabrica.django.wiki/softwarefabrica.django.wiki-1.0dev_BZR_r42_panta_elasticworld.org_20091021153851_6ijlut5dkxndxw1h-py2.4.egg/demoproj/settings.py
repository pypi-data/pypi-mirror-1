#!/usr/bin/env python
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved

"""
settings.py

softwarefabrica wiki demo project django settings file.

@author: Marco Pantaleoni
@contact: Marco Pantaleoni <panta@elasticworld.org>
@contact: Marco Pantaleoni <marco.pantaleoni@gmail.com>
@copyright: Copyright (C) 2008 Marco Pantaleoni. All rights reserved.
"""

# -- calculate project root ----------------------------------------------
import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
# ------------------------------------------------------------------------

DEBUG          = True
#DEBUG          = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
    ('Demo User', 'demo@demo.test'),
)
MANAGERS = ADMINS

# e-mail support
# EMAIL_HOST = ""
# EMAIL_HOST_USER = ""
# EMAIL_HOST_PASSWORD = ""

DATABASE_ENGINE   = 'sqlite3'      # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME     = os.path.join(PROJECT_ROOT, 'demo.db') # Or path to database file if using sqlite3.
DATABASE_USER     = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''             # Not used with sqlite3.
DATABASE_HOST     = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT     = ''             # Set to empty string for default. Not used with sqlite3.

#DATABASE_ENGINE   = 'mysql'
#DATABASE_NAME     = 'sfwikidemo'
#DATABASE_USER     = 'root'
#DATABASE_PASSWORD = ''
#DATABASE_HOST     = 'localhost'
#DATABASE_PORT     = '3306'

#DATABASE_ENGINE   = 'postgresql_psycopg2'
#DATABASE_NAME     = 'sfwikidemo'
#DATABASE_USER     = 'postgres'
#DATABASE_PASSWORD = ''
#DATABASE_HOST     = 'localhost'
#DATABASE_PORT     = '5432'

DEFAULT_CHARSET = 'utf-8'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Chicago'
#TIME_ZONE = 'Europe/Rome'
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'it'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# upload, static and admin media directories
UPLOAD_MEDIA_DIR   = os.path.join(PROJECT_ROOT, 'upload_media') # where static *uploaded* media files resided
STATIC_MEDIA_DIR   = os.path.join(PROJECT_ROOT, 'static_media') # where static files reside
ADMIN_MEDIA_DIR    = os.path.join(PROJECT_ROOT, 'admin_media')  # admin media files

# base url
WEBSITE_URL         = 'http://wiki.demo.test'
UPLOAD_MEDIA_URL    = '/uploads/'       # urlparse.urljoin() used -> use 'http://.../' or '/RELATIVE/' (strictly!)
ADMIN_MEDIA_PREFIX  = '/admin_media/'   # URL prefix for admin media -- CSS, JavaScript and images. (Trailing '/')
UPLOAD_MEDIA_PREFIX = '/uploads'        # no trailing '/' !
STATIC_MEDIA_PREFIX = '/static'         # no trailing '/' !

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = UPLOAD_MEDIA_DIR

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = UPLOAD_MEDIA_URL

STATIC_ROOT = STATIC_MEDIA_DIR
STATIC_URL  = STATIC_MEDIA_PREFIX + '/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = ADMIN_MEDIA_PREFIX

LOGIN_URL = '/login'

#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

# AUTH_PROFILE_MODULE  -- for Django User extension
# see http://www.b-list.org/weblog/2006/06/06/django-tips-extending-user-model
#AUTH_PROFILE_MODULE = 'xxx.UserProfile'

#import logging
#LOG_FILE  = "/tmp/demoproj.log"
#LOG_LEVEL = logging.INFO

# Make this unique, and don't share it with anybody.
SECRET_KEY = '95a5G32%!6@rhfb7%^6ofud1&1#17^jKJ!&5#vb$!$dhg!6s23'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# A tuple of callables that are used to populate the context in RequestContext.
# These callables take a request object as their argument and return a dictionary
# of items to be merged into the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'softwarefabrica.django.utils.viewshelpers.context_vars',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'demoproj.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.markup',
    'softwarefabrica.django.utils',
    'softwarefabrica.django.forms',
    'softwarefabrica.django.crud',
    'softwarefabrica.django.wiki',
)
