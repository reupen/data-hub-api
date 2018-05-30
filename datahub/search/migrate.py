from logging import getLogger

from datahub.core.exceptions import DataHubException
from datahub.search.apps import get_search_apps
from datahub.search.elasticsearch import start_alias_transaction
from datahub.search.tasks import migrate_model

logger = getLogger(__name__)


def migrate_apps(app_names=None):
    """Migrates all search apps to new indices if their mappings are out of date."""
    logger.info('Starting search app migration')
    apps = get_search_apps()
    apps_to_migrate = [app for app in apps if app.name in app_names] if app_names else apps
    for app in apps_to_migrate:
        migrate_app(app)


def migrate_app(search_app):
    """Migrates a search app to a new index (if its mapping is out of date)."""
    app_name = search_app.name
    es_model = search_app.es_model

    search_app.init_es()

    target_mapping_hash = es_model.get_target_mapping_hash()
    needs_migration = es_model.get_current_mapping_hash() != target_mapping_hash
    if needs_migration:
        _perform_migration(search_app)
        return

    if len(es_model.get_read_indices()) != 1:
        logger.info('Possibly incomplete %s search app migration detected', app_name)
        _schedule_resync(search_app)
        return

    logger.info('%s search app is up to date', app_name)


def _perform_migration(search_app):
    app_name = search_app.name
    es_model = search_app.es_model
    logger.info('Migrating the %s search app', app_name)

    read_alias_name = es_model.get_read_alias()
    write_alias_name = es_model.get_write_alias()
    new_index_name = es_model.get_target_index_name()

    current_read_indices = es_model.get_read_indices()
    current_write_index = es_model.get_write_index()

    if current_write_index not in current_read_indices:
        raise DataHubException('Cannot migrate Elasticsearch index with a read alias referencing '
                               'a different index to the write alias')

    logger.info('Updating aliases for the %s search app', app_name)

    es_model.create_index(new_index_name)

    with start_alias_transaction() as alias_transaction:
        alias_transaction.add_indices_to_alias(read_alias_name, [new_index_name])
        alias_transaction.add_indices_to_alias(write_alias_name, [new_index_name])
        alias_transaction.remove_indices_from_alias(write_alias_name, [current_write_index])

    _schedule_resync(search_app)


def _schedule_resync(search_app):
    logger.info(
        'Scheduling resync and clean-up for the %s search app',
        search_app.name,
    )
    migrate_model.apply_async(
        args=(search_app.name, search_app.es_model.get_target_mapping_hash())
    )
