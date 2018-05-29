from logging import getLogger

from datahub.core.utils import slice_iterable_into_chunks
from datahub.search.elasticsearch import bulk

logger = getLogger(__name__)

PROGRESS_INTERVAL = 20000


def sync_app(item, batch_size=None):
    """Syncs objects for an app to ElasticSearch in batches of batch_size."""
    model_name = item.es_model.__name__
    batch_size = batch_size or item.bulk_batch_size
    logger.info(f'Processing {model_name} records, using batch size {batch_size}')

    rows_processed = 0
    total_rows = item.queryset.count()
    it = item.queryset.iterator(chunk_size=batch_size)
    batches = slice_iterable_into_chunks(it, batch_size)
    for batch in batches:
        actions = list(item.es_model.db_objects_to_es_documents(batch))
        num_actions = len(actions)
        bulk(
            actions=actions,
            chunk_size=num_actions,
            request_timeout=300,
            raise_on_error=True,
            raise_on_exception=True,
        )

        emit_progress = (
            (rows_processed + num_actions) // PROGRESS_INTERVAL
            - rows_processed // PROGRESS_INTERVAL
            > 0
        )

        rows_processed += num_actions

        if emit_progress:
            logger.info(f'{model_name} rows processed: {rows_processed}/{total_rows} '
                        f'{rows_processed*100//total_rows}%')

    logger.info(f'{model_name} rows processed: {rows_processed}/{total_rows} 100%.')
