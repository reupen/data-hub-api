# Generated by Django 2.1 on 2018-08-23 18:23
from pathlib import PurePath

from django.db import migrations
from django.db.migrations import RunPython
from datahub.core.migration_utils import load_yaml_data_in_migration


def load_evidence_tags(apps, schema_editor):
    load_yaml_data_in_migration(
        apps,
        PurePath(__file__).parent / '0003_initial_evidence_tags.yaml'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('evidence', '0002_evidencedocument_permissions'),
    ]

    operations = [
        RunPython(load_evidence_tags, RunPython.noop),
    ]
