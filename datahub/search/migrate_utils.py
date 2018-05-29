from logging import getLogger

from datahub.core.exceptions import DataHubException
from datahub.search.bulk_sync import sync_app
from datahub.search.elasticsearch import (
    delete_index,
    get_aliases_for_index,
    update_alias,
)


logger = getLogger(__name__)


def resync_after_migrate(search_app):
    """Resyncs all documents in an index following a migration."""
    sync_app(search_app)

    es_model = search_app.es_model
    read_alias = es_model.get_read_alias()
    read_indices = es_model.get_read_indices()
    write_index = es_model.get_write_index()

    if write_index not in read_indices:
        raise DataHubException('Write index not in read alias, aborting mapping migration...')

    indices_to_remove = read_indices - {write_index}

    if indices_to_remove:
        update_alias(read_alias, remove_indices=tuple(indices_to_remove))
    else:
        logger.warning('No indices to remove for the {read_alias} alias')

    for index in indices_to_remove:
        _delete_old_index(index)


def _delete_old_index(index):
    if not get_aliases_for_index(index):
        delete_index(index)
