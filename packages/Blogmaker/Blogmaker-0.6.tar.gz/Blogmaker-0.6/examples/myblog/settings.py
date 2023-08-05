# Django settings for farmdev_blogmaker project.
import os, django, inspect

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEMPLATE_STRING_IF_INVALID = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = os.path.abspath('./myblog.db')             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you include images in your blog entries, you should set ``MEDIA_ROOT`` and ``MEDIA_URL`` as described in the `Django documentation <http://www.djangoproject.com/documentation/0.96/settings/#media-root>`_. You must also configure your server to serve files from ``MEDIA_ROOT`` at ``MEDIA_URL``.

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/custom/'

# URL prefix for where you will serve the media directory contained at blogmaker.blog.media, 
# e.g. "/media/blog/", "http://foo.com/media/blog/"
BLOG_MEDIA_PREFIX = '/media/blog/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')7y=@4z%r9((monawppdq^gn$bnkuypew%0^w+rdjalech*+bw'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
# Blogmaker's comment application requires that ``django.core.context_processors.request`` be one of your installed context processors. This puts a ``request`` object in the context. The comment honeypot uses this to access the IP address of a request.
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.auth',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'myblog.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.markup',
    'django.contrib.admin',
    'blogmaker.blog',
    'blogmaker.comments',
    'blogmaker.util',
)

# The id of the primary blog user, as defined by the Django Auth/User model.
DEFAULT_BLOG_USER = 'kumar'

# The directory where log files will be written.
LOG_DIRECTORY = os.path.dirname(__file__)

# Your copyright text, e.g. "All contents Copyright 2007, Acme Inc."
COPYRIGHT = ''

# Defines the root URL of your site, e.g. http://domain.com/
SITE_ROOT = 'http://127.0.0.1:8000/'

# Defines the root URL for the blog path, e.g. if you want the blog to live at http://domain.com/blog/, this variable would be set to '/blog/'. If you want the blog to live at a different subdomain than the rest of the site, you will need to set an absolute URL: 'http://blog.domain.com/'
BLOG_ROOT = '/blog/'

# The following should be set if you enable email notification for comment/trackback features:

# A list of ``('Name', 'email address')`` tuples defining the people to whom notification emails will be sent.
MANAGERS = [('Kumar McMillan', 'kumar.mcmillan@gmail.com')]

# The default e-mail you would like e-mails to be sent from.
DEFAULT_FROM_EMAIL = 'kumar.mcmillan@gmail.com'
