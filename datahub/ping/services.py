from logging import getLogger

from django.conf import settings
from django.db import DatabaseError
from elasticsearch.exceptions import ConnectionError as ESConnectionError
from raven.contrib.django.raven_compat.models import client as raven_client

from datahub.company.models import Company
from datahub.search.elasticsearch import index_exists


logger = getLogger(__name__)


class CheckDatabase:
    """Check the database is up and running."""

    name = 'database'

    def check(self):
        """Perform the check."""
        try:
            Company.objects.all().exists()
            return True, ''
        except DatabaseError as e:
            msg = 'Cannot connect to the database.'
            logger.exception(msg)
            raven_client.captureException()
            return False, msg


class CheckES:
    """Check Elasticsearch is up and running."""

    name = 'elasticsearch'

    def check(self):
        """Perform the check."""
        try:
            if index_exists(settings.ES_INDEX):
                return True, ''
            else:
                return False, 'ES index does not exist'
        except ESConnectionError as e:
            msg = 'Cannot connect to ES'
            logger.exception(msg)
            raven_client.captureException()
            return False, msg


services_to_check = (CheckDatabase, CheckES)
