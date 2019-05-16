# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-05-07 03:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0165_auto_20190503_1352'),
    ]

    operations = [
        migrations.RenameField(
            model_name='applicationformdatarecord',
            old_name='comment',
            new_name='assessor_comment',
        ),
        migrations.AddField(
            model_name='applicationformdatarecord',
            name='officer_comment',
            field=models.TextField(blank=True),
        ),
    ]
