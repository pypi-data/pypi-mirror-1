import os

DEBUG = TEMPLATE_DEBUG = True
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/shorturls.db'
INSTALLED_APPS = ('django_feedburner',)
ROOT_URLCONF = 'django_feedburner.tests.urls'
TEMPLATE_DIRS = os.path.join(os.path.dirname(__file__), 'tests', 'templates')


FEEDBURNER_URLS = {
    '/feeds/numbers/': '/numbers',
    '/feeds/wrongfeed/': '/wrongfeed',
}
