# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-09-20 08:18
from __future__ import unicode_literals

from django.db import migrations, models

def content_forward(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    db_alias = schema_editor.connection.alias

    invoice_qs = ContentType.objects.using(db_alias).filter(app_label='invoice', model__in=('invoicebpay', 'invoice'))
    invoice_qs.update(app_label='payments')


def content_reverse(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    db_alias = schema_editor.connection.alias

    invoice_qs = ContentType.objects.using(db_alias).filter(app_label='payments', model__in=('invoicebpay', 'invoice'))
    invoice_qs.update(app_label='invoice')


class Migration(migrations.Migration):

    dependencies = [
        ('cash', '0010_parkstay_rebase'),
        ('invoice', '0006_invoicebpay'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='voided',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='token',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterModelTable(
            name='InvoiceBPAY',
            table='payments_invoicebpay',
        ),
        migrations.AlterModelTable(
            name='Invoice',
            table='payments_invoice',
        ),
        #migrations.RunPython(
        #    code=content_forward,
        #    reverse_code=content_reverse,
        #),
    ]
