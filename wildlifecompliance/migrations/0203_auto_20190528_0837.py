# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-05-28 00:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0202_auto_20190524_1724'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='compliancepermissiongroup',
            options={'default_permissions': (), 'verbose_name': 'CM_Compliance Permission group', 'verbose_name_plural': 'CM_Compliance permission groups'},
        ),
        migrations.AlterModelOptions(
            name='regiondistrict',
            options={'verbose_name': 'CM_Region District', 'verbose_name_plural': 'CM_Region Districts'},
        ),
        migrations.RenameField(
            model_name='regiondistrict',
            old_name='name',
            new_name='district',
        ),
        migrations.AddField(
            model_name='regiondistrict',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wildlifecompliance.RegionDistrict'),
        ),
    ]
