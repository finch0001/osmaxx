# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-16 07:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('excerptexport', '0049_set_removal_date_for_existing_files_20160615_1359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extractionorder',
            name='download_status',
        ),
    ]
