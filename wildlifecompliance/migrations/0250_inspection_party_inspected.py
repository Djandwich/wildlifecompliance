# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-07-15 05:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0249_merge_20190712_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspection',
            name='party_inspected',
            field=models.CharField(choices=[('person', 'Person'), ('organisation', 'Organisation')], default='person', max_length=30),
        ),
    ]
