# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-31 13:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0001_squashed_0013_add_quotable_as_case_study'),
        ('interaction', '0001_squash_0008_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='interaction',
            name='investment_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='investment.InvestmentProject'),
        ),
    ]
