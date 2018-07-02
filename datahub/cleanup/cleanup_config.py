from enum import Enum

_registry = {}


class CleanupType(Enum):
    """Type of clean-up operation."""

    # Orphaned records that haven't been modified for a period of time and should be deleted
    orphaned = 'orphaned'
    # Records that haven't been modified for a long period of time (e.g. 10 years) and should be
    # deleted
    very_old = 'very-old'


class CleanupConfig:
    """
    Configuration for a clean-up operation.

    Contains the parameters used to determine whether a clean-up task should operate on a record.
    """

    age_threshold = 30 * 6  # 6 months
    date_field = 'modified_on'


def register_config(cleanup_type, model):
    """Registers a clean-up configuration."""
    def decorator(config):
        key = (cleanup_type, model)
        if key in _registry:
            raise ValueError(f'A clean-up configuration was already registered for key {key}.')
        _registry[key] = config
        return config

    return decorator


def get_configs_for_type(cleanup_type):
    """Gets the registered CleanupConfigs for a CleanupType."""
    return {
        model: config for (item_cleanup_type, model), config in _registry.items()
        if item_cleanup_type == cleanup_type
    }


def get_config_for_type_and_model(cleanup_type, model):
    """Gets the registered CleanupConfig for a CleanupType and model."""
    return _registry[(cleanup_type, model)]
