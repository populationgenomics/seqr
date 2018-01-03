# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-18 04:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0031_auto_20171214_1104'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ElasticsearchDataset',
        ),
        migrations.AddField(
            model_name='dataset',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dataset',
            name='name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dataset',
            name='status',
            field=models.CharField(blank=True, choices=[(b'Q', b'Queued'), (b'G', b'Loading'), (b'L', b'Loaded'), (b'F', b'Failed')], db_index=True, max_length=1, null=True),
        ),
    ]
