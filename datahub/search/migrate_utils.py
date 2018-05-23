from datahub.search.bulk_sync import sync_app
from datahub.search.elasticsearch import (
    delete_index,
    get_aliases_for_index,
    get_indices_for_alias,
    update_alias,
)


def resync_after_migrate(search_app):
    """Resyncs all documents in an index following a migration."""
    sync_app(search_app)

    read_alias = search_app.es_model.get_read_alias()
    write_alias = search_app.es_model.get_write_alias()

    indices_to_remove = get_indices_for_alias(read_alias) - get_indices_for_alias(write_alias)

    update_alias(read_alias, remove_indices=tuple(indices_to_remove))

    for index in indices_to_remove:
        _delete_old_index(index)


def _delete_old_index(index):
    if not get_aliases_for_index(index):
        delete_index(index)
