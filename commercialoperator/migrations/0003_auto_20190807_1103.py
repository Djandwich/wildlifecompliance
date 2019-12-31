# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-08-07 03:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commercialoperator', '0002_auto_20190801_0939'),
    ]

    operations = [
        migrations.RenameField(
            model_name='applicationtype',
            old_name='oracle_code',
            new_name='oracle_code_application',
        ),
        migrations.AddField(
            model_name='applicationtype',
            name='oracle_code_licence',
            field=models.CharField(default='GGE53 EXEMPT', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='park',
            name='is_gst_exempt',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]