import os
DIRNAME = os.path.dirname(__file__)

DEFAULT_CHARSET = 'utf-8'

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(DIRNAME, 'drilldown_test.db')

#DATABASE_ENGINE = 'mysql'
#DATABASE_NAME = 'drilldown_test'
#DATABASE_USER = 'root'
#DATABASE_PASSWORD = ''
#DATABASE_HOST = 'localhost'
#DATABASE_PORT = '3306'

#DATABASE_ENGINE = 'postgresql_psycopg2'
#DATABASE_NAME = 'drilldown_test'
#DATABASE_USER = 'postgres'
#DATABASE_PASSWORD = ''
#DATABASE_HOST = 'localhost'
#DATABASE_PORT = '5432'

TEMPLATE_DEBUG = True
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)
TEMPLATE_DIRS = (
    os.path.join(DIRNAME, 'templates'),
    )

SITE_ID = 1

#TEST_RUNNER = 'softwarefabrica.django.drilldown.tests.runner.run_tests'
TEST_RUNNER = 'django-test-coverage.runner.run_tests'

TEST_APPS   = ('tests',)
COVERAGE_MODULES = ('softwarefabrica.django.drilldown.models',)

import logging
if not hasattr(logging, 'VERBOSE'):
    logging.VERBOSE = 15  # intermediate between DEBUG and INFO
    logging._levelNames['VERBOSE'] = logging.VERBOSE
    logging._levelNames[logging.VERBOSE] = 'VERBOSE'
#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.VERBOSE)
logging.basicConfig(level=logging.DEBUG)

ROOT_URLCONF = 'softwarefabrica.django.drilldown.tests.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'softwarefabrica.django.utils',
    'softwarefabrica.django.forms',
    'softwarefabrica.django.crud',
    'softwarefabrica.django.common',
    'softwarefabrica.django.drilldown',
    'softwarefabrica.django.drilldown.tests',
)
