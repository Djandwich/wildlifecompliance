# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-06-05 08:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wildlifecompliance', '0215_callemail_allocated_to'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='callemail',
            name='assigned_to',
        ),
        migrations.AddField(
            model_name='callemail',
            name='assigned_to',
            field=models.ManyToManyField(blank=True, related_name='callemail_assigned_to', to=settings.AUTH_USER_MODEL),
        ),
    ]
