from datetime import timedelta

from elasticsearch import TransportError
from raven.contrib.django.models import client as raven

from datahub.search.bulk_sync import sync_app
from datahub.search.elasticsearch import (
    delete_index,
    get_aliases_for_index,
    get_client,
    get_indices_for_alias,
    index_exists,
    update_alias,
)

DEFAULT_REINDEX_TIMEOUT = int(timedelta(hours=2).total_seconds())


def reindex_model(search_app, old_index, new_index, timeout=DEFAULT_REINDEX_TIMEOUT):
    """Copies documents from one Elasticsearch index to another."""
    client = get_client()
    try:
        client.reindex(
            body={
                'source': {
                    'index': old_index,
                    'type': search_app.es_model._doc_type.name,
                },
                'dest': {
                    'index': new_index,
                }
            },
            request_timeout=timeout,
            refresh=True,
        )
    except TransportError:
        raven.captureException('Elasticsearch reindex failed, continuing with full resync...')
    else:
        _remove_index_from_old_alias(old_index, search_app.es_model.get_read_alias())
        _delete_old_index(old_index)


def resync_after_migrate(search_app, old_index):
    """Resyncs all documents in an index following a migration."""
    sync_app(search_app)

    read_alias = search_app.es_model.get_read_alias()

    if old_index in get_indices_for_alias(read_alias):
        _remove_index_from_old_alias(old_index, read_alias)

    if index_exists(old_index):
        _delete_old_index(old_index)


def _remove_index_from_old_alias(index, alias):
    update_alias(alias, remove_indices=(index,))


def _delete_old_index(index):
    if not get_aliases_for_index(index):
        delete_index(index)
