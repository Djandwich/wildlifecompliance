# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-10-17 06:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0313_auto_20191017_1152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sanctionoutcomeuseraction',
            name='who',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
