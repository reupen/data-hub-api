from logging import getLogger

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
    indices_to_remove = es_model.get_read_indices() - {es_model.get_write_index()}

    if indices_to_remove:
        update_alias(read_alias, remove_indices=tuple(indices_to_remove))
    else:
        logger.warning('No indices to remove for the {read_alias} alias')

    for index in indices_to_remove:
        _delete_old_index(index)


def _delete_old_index(index):
    if not get_aliases_for_index(index):
        delete_index(index)
