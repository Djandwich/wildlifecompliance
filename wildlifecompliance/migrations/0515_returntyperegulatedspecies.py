# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-09-03 02:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0514_merge_20200831_0924'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReturnTypeRegulatedSpecies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('species_name', models.CharField(max_length=100)),
                ('species_price', models.DecimalField(decimal_places=2, default='0', max_digits=8)),
                ('return_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='regulated_species', to='wildlifecompliance.ReturnType')),
            ],
            options={
                'verbose_name': 'Regulated Species',
                'verbose_name_plural': 'Regulated Species',
            },
        ),
    ]
