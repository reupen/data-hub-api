# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-16 14:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0023_populate_public_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='public_token',
            field=models.CharField(help_text='Used for public facing access.', max_length=100, unique=True),
        ),
    ]
