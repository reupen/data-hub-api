from logging import getLogger

from datahub.core.exceptions import DataHubException
from datahub.search.apps import get_search_apps
from datahub.search.elasticsearch import update_alias
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
    es_model = search_app.es_model
    app_name = search_app.name

    search_app.init_es()

    # TODO: Compare the mappings and work out if only fields have been added. (Just update the
    # mapping and resync in that case.)

    needs_migration = es_model.get_current_mapping_hash() != es_model.get_target_mapping_hash()
    if not needs_migration:
        logger.info('%s search app index is up to date', app_name)
        return

    logger.info('Migrating the %s search app', app_name)

    read_alias_name = es_model.get_read_alias()
    write_alias_name = es_model.get_write_alias()
    new_index_name = es_model.get_target_index_name()

    current_read_indices = es_model.get_read_indices()
    current_write_index = es_model.get_write_index()

    if current_write_index not in current_read_indices:
        raise DataHubException('Cannot migrate Elasticsearch index with read alias referencing '
                               'a different index to write alias')

    logger.info('Updating aliases for the %s search app', app_name)

    update_alias(read_alias_name, add_indices=(new_index_name,))
    update_alias(
        write_alias_name,
        add_indices=(new_index_name,),
        remove_indices=(current_write_index,)
    )

    # FIXME
    search_app_cls_path = f'{search_app.__class__.__module__}.{search_app.__class__.__name__}'

    logger.info('Submitting resync task for the %s search app to Celery', app_name)

    migrate_model.apply_async(
        args=(search_app_cls_path,)
    )
