# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-09-26 02:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
#        ('mooring', '0040_updateviews'),
        ('mooring', '0064_auto_20180920_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='send_invoice',
            field=models.BooleanField(default=False),
        ),
    ]
