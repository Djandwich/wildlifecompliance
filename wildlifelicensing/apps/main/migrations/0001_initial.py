# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-10 08:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('licence', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessorGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('purpose', models.BooleanField(default=False)),
                ('members', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('code', models.CharField(max_length=10, unique=True)),
                ('one_off', models.BooleanField(default=False)),
                ('obsolete', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DefaultCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wl_main.Condition')),
            ],
        ),
        migrations.CreateModel(
            name='WildlifeLicence',
            fields=[
                ('licence_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='licence.Licence')),
                ('sequence_number', models.IntegerField(default=1)),
                ('purpose', models.TextField(blank=True)),
                ('cover_letter_message', models.TextField(blank=True)),
                ('return_frequency', models.IntegerField(choices=[(-1, 'One off'), (1, 'Monthly'), (3, 'Quarterly'), (6, 'Twice-Yearly'), (12, 'Yearly')], default=-1)),
                ('cover_letter_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cover_letter_document', to='accounts.Document')),
                ('licence_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='licence_document', to='accounts.Document')),
                ('previous_licence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wl_main.WildlifeLicence')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Profile')),
            ],
            options={
                'abstract': False,
            },
            bases=('licence.licence',),
        ),
        migrations.CreateModel(
            name='WildlifeLicenceType',
            fields=[
                ('licencetype_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='licence.LicenceType')),
                ('identification_required', models.BooleanField(default=False)),
                ('default_conditions', models.ManyToManyField(blank=True, through='wl_main.DefaultCondition', to='wl_main.Condition')),
                ('code_slug', models.SlugField(max_length=64)),
            ],
            options={
                'abstract': False,
            },
            bases=('licence.licencetype',),
        ),
        migrations.AddField(
            model_name='defaultcondition',
            name='wildlife_licence_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wl_main.WildlifeLicenceType'),
        ),
        migrations.AlterUniqueTogether(
            name='defaultcondition',
            unique_together=set([('condition', 'wildlife_licence_type', 'order')]),
        ),
    ]
