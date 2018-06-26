import environ

environ.Env.read_env()  # reads the .env file
env = environ.Env()

from .common import *

# We need to prevent Django from initialising datahub.search for tests.
# Removing SearchConfig stops django from calling .ready() which initialises
# the search signals
INSTALLED_APPS.remove('datahub.search.apps.SearchConfig')
INSTALLED_APPS += [
    'datahub.search',
    'datahub.core.test.support',
    'datahub.documents.test.my_entity_document',
    'datahub.search.test.search_support',
]

SEARCH_APPS += [
    'datahub.search.test.search_support.simplemodel.SimpleModelSearchApp',
]

# The index is set dynamically in datahub/search/conftest.py, so that tests can be parallelised.
ES_INDEX_PREFIX = None
ES_INDEX_SETTINGS = {
    **ES_INDEX_SETTINGS,
    'number_of_shards': 1,
    'number_of_replicas': 0,
}
DOCUMENT_BUCKET='test-bucket'
AV_SERVICE_URL='http://av-service/'

DATA_SCIENCE_COMPANY_API_URL = 'http://company-timeline/'
DATA_SCIENCE_COMPANY_API_ID = 'company-timeline-api-id'
DATA_SCIENCE_COMPANY_API_KEY = 'company-timeline-api-key'

OMIS_GENERIC_CONTACT_EMAIL = 'omis@example.com'
OMIS_NOTIFICATION_OVERRIDE_RECIPIENT_EMAIL = ''
OMIS_NOTIFICATION_ADMIN_EMAIL = 'fake-omis-admin@digital.trade.gov.uk'
OMIS_NOTIFICATION_API_KEY = ''

GOVUK_PAY_URL='https://payments.example.com/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }
}

CELERY_TASK_ALWAYS_EAGER = True

ACTIVITY_STREAM_IP_WHITELIST = '1.2.3.4'
ACTIVITY_STREAM_ACCESS_KEY_ID = 'some-id'
ACTIVITY_STREAM_SECRET_ACCESS_KEY = 'some-secret'

DOCUMENT_BUCKETS = {
    'default': {
        'bucket': 'foo',
        'aws_access_key_id': 'bar',
        'aws_secret_access_key': 'baz',
        'aws_region': 'eu-west-2',
    },
    'investment': {
        'bucket': 'foo',
        'aws_access_key_id': 'bar',
        'aws_secret_access_key': 'baz',
        'aws_region': 'eu-west-2',
    },
    'report': {
        'bucket': 'foo',
        'aws_access_key_id': 'bar',
        'aws_secret_access_key': 'baz',
        'aws_region': 'eu-west-2',
    }
}
