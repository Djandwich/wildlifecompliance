# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-07-15 05:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0251_auto_20190715_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspection',
            name='party_inspected',
            field=models.CharField(choices=[('individual', 'individual'), ('organisation', 'organisation')], default='person', max_length=30),
        ),
    ]
