# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-06-05 03:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0213_auto_20190530_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='callemail',
            name='district',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='callemail_district', to='wildlifecompliance.RegionDistrict'),
        ),
        migrations.AddField(
            model_name='callemail',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='callemail_region', to='wildlifecompliance.RegionDistrict'),
        ),
        migrations.AlterField(
            model_name='complianceworkflowlogentry',
            name='district',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='callemail_workflow_district', to='wildlifecompliance.RegionDistrict'),
        ),
        migrations.AlterField(
            model_name='complianceworkflowlogentry',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='callemail_workflow_region', to='wildlifecompliance.RegionDistrict'),
        ),
    ]
