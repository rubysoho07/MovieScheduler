# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-24 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler_core', '0003_auto_20170321_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movieschedule',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
