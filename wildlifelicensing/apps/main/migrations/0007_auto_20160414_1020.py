# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-14 02:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_assessordepartment'),
    ]

    operations = [
        migrations.AddField(
            model_name='condition',
            name='code',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='condition',
            name='one_off',
            field=models.BooleanField(default=False),
        ),
    ]