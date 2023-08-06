# django-djangoplus setup
# First version of this file done by Guilherme Semente

# Downloads setuptools if not find it before try to import
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup
from djangoplus import get_version

setup(
    name = 'django-plus',
    version = get_version(),
    description = 'Django utilities library',
    long_description = 'django-plus is a library containing a coupple of utilities for Django developers.',
    author = 'Marinho Brandao',
    author_email = 'marinho@gmail.com',
    url = 'http://django-plus.googlecode.com',
    license = 'GNU Lesser General Public License (LGPL)',
    packages = ['djangoplus', 'djangoplus.templatetags',
        'djangoplus.fieldtypes','djangoplus.forms','djangoplus.middleware',
        'djangoplus.shortcuts','djangoplus.templates',
        'djangoplus.templates.admin','djangoplus.templates.admin.djangoplus',
        'djangoplus.templates.admin.djangoplus.dynamictemplate',
        'djangoplus.templates.djangoplus','djangoplus.tests',
        'djangoplus.utils','djangoplus.views','djangoplus.widgets',],
)
