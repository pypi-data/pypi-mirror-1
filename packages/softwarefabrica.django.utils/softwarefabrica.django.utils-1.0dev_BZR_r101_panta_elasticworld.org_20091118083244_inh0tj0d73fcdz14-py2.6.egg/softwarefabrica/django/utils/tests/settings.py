import os
DIRNAME = os.path.dirname(__file__)

DEFAULT_CHARSET = 'utf-8'

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(DIRNAME, 'utils_test.db')

#DATABASE_ENGINE = 'mysql'
#DATABASE_NAME = 'utils_test'
#DATABASE_USER = 'root'
#DATABASE_PASSWORD = ''
#DATABASE_HOST = 'localhost'
#DATABASE_PORT = '3306'

#DATABASE_ENGINE = 'postgresql_psycopg2'
#DATABASE_NAME = 'utils_test'
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

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'softwarefabrica.django.utils',
    'softwarefabrica.django.utils.tests',
)
