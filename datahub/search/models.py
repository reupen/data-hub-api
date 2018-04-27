from hashlib import blake2b

from django.conf import settings
from elasticsearch_dsl import DocType, MetaField

from datahub.core.exceptions import DataHubException
from datahub.search.elasticsearch import (
    alias_exists, create_index, get_indices_for_alias, index_exists, update_alias
)
from datahub.search.utils import get_model_non_mapped_field_names, get_normalised_mapping_as_bytes


class BaseESModel(DocType):
    """Helps convert Django models to dictionaries."""

    MAPPINGS = {}

    COMPUTED_MAPPINGS = {}

    SEARCH_FIELDS = ()

    class Meta:
        dynamic = MetaField('false')

    @classmethod
    def get_read_alias(cls):
        """Gets the alias to be used for read operations."""
        return f'{settings.ES_INDEX}-{cls._doc_type.name}-read'

    @classmethod
    def get_write_alias(cls):
        """Gets the alias to be used for write operations."""
        return f'{settings.ES_INDEX}-{cls._doc_type.name}-write'

    @classmethod
    def get_read_indices(cls):
        """Gets the indices currently referenced by the read alias."""
        return get_indices_for_alias(cls.get_read_alias())

    @classmethod
    def get_write_index(cls):
        """Gets the index currently referenced by the write alias."""
        indices = get_indices_for_alias(cls.get_write_alias())
        if len(indices) != 1:
            raise DataHubException()
        return indices[0]

    @classmethod
    def get_index_prefix(cls):
        """Gets the prefix used for indices and aliases."""
        return f'{settings.ES_INDEX}-{cls._doc_type.name}-'

    @classmethod
    def get_target_mapping_hash(cls):
        """Gets a unique hash digest for mapping (as defined in the code base)."""
        mapping_data = get_normalised_mapping_as_bytes(cls._doc_type.mapping.to_dict())
        return blake2b(mapping_data, digest_size=16).hexdigest()

    @classmethod
    def get_current_mapping_hash(cls):
        """Extracts and returns the mapping hash from the current index name."""
        current_write_index = cls.get_write_index()
        prefix = cls.get_index_prefix()
        if not current_write_index.startswith(prefix):
            return ''
        return current_write_index[len(prefix):]

    @classmethod
    def get_target_index_name(cls):
        """Generates a unique name for the index based on its mapping."""
        mapping_hash = cls.get_target_mapping_hash()
        prefix = cls.get_index_prefix()
        return f'{prefix}{mapping_hash}'

    @classmethod
    def configure_index(cls):
        """Configures Elasticsearch index."""
        # TODO: Handle migration from single index?

        index_name = cls.get_target_index_name()
        if not index_exists(index_name):
            create_index(index_name, index_settings=settings.ES_INDEX_SETTINGS)
            cls.init(index_name)

        if not alias_exists(cls.get_read_alias()):
            update_alias(cls.get_read_alias(), add_indices=(index_name,))

        if not alias_exists(cls.get_write_alias()):
            update_alias(cls.get_write_alias(), add_indices=(index_name,))

    @classmethod
    def es_document(cls, dbmodel):
        """Creates Elasticsearch document."""
        source = cls.db_object_to_dict(dbmodel)

        return {
            '_index': cls.get_write_alias(),
            '_type': cls._doc_type.name,
            '_id': source.get('id'),
            '_source': source,
        }

    @classmethod
    def db_object_to_dict(cls, dbmodel):
        """Converts a DB model object to a dictionary suitable for Elasticsearch."""
        mapped_values = (
            (col, fn, getattr(dbmodel, col)) for col, fn in cls.MAPPINGS.items()
        )
        fields = get_model_non_mapped_field_names(cls)

        result = {
            **{col: fn(val) if val is not None else None for col, fn, val in mapped_values},
            **{col: fn(dbmodel) for col, fn in cls.COMPUTED_MAPPINGS.items()},
            **{field: getattr(dbmodel, field) for field in fields},
        }

        return result

    @classmethod
    def db_objects_to_es_documents(cls, dbmodels):
        """Converts DB model objects to Elasticsearch documents."""
        for dbmodel in dbmodels:
            yield cls.es_document(dbmodel)
