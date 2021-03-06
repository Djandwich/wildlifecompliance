# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-10-07 03:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0186_auto_20190808_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationcondition',
            name='is_rendered',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='applicationcondition',
            name='return_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wildlifecompliance.ReturnType'),
        ),
        migrations.AlterField(
            model_name='applicationstandardcondition',
            name='return_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wildlifecompliance.ReturnType'),
        ),
        migrations.AlterField(
            model_name='defaultcondition',
            name='return_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wildlifecompliance.ReturnType'),
        ),
    ]
