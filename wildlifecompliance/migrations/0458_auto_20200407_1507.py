# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-04-07 07:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0457_merge_20200331_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legalcaseuseraction',
            name='who',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
