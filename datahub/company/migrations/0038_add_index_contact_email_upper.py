# Generated by Django 2.1.2 on 2018-10-16 09:52

"""
Creates an index on UPPER(email) on the Contact model (for use with the iexact filter look-up).

As Django does not support creating indexes on expressions, SQL is used.

The migration is run inside a transaction, so CREATE INDEX CONCURRENTLY is not used.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0037_remove_contact_contactable_columns'),
    ]

    operations = [
        migrations.RunSQL(
            [
                'CREATE INDEX "company_contact_upper_email_244368" '
                'ON "company_contact" (UPPER("email"));'
            ],
            reverse_sql=[
                'DROP INDEX "company_contact_upper_email_244368";'
            ],
        )
    ]
