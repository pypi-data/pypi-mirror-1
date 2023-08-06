# Django settings for testproj project.

import os
import sys
# import source code dir
sys.path.insert(0, os.path.join(os.getcwd(), os.pardir))

SITE_ID = 300

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = "urls"

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

TEST_RUNNER = "celery.tests.runners.run_tests"
TEST_APPS = (
    "celery",
)
COVERAGE_EXCLUDE_MODULES = ("celery.__init__",
                            "celery.conf",
                            "celery.tests.*",
                            "celery.management.*",
                            "celery.contrib.*",
                            "celery.bin.*",
                            "celery.utils.patch",
                            "celery.utils.compat",
                            "celery.task.rest",
                            "celery.platform", # FIXME
                            "celery.backends.mongodb", # FIXME
                            "celery.backends.tyrant", # FIXME
                            )
COVERAGE_HTML_REPORT = True
COVERAGE_BRANCH_COVERAGE = True

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"

TT_HOST = "localhost"
TT_PORT = 1978

CELERY_DEFAULT_EXCHANGE = "testcelery"
CELERY_DEFAULT_ROUTING_KEY = "testcelery"
CELERY_DEFAULT_QUEUE = "testcelery"

CELERY_QUEUES = {"testcelery": {"binding_key": "testcelery"}}

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'testdb.sqlite'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'celery',
    'someapp',
    'someappwotask',
)

try:
    import test_extensions
except ImportError:
    pass
else:
    pass
    INSTALLED_APPS += ("test_extensions", )

CELERY_SEND_TASK_ERROR_EMAILS = False
