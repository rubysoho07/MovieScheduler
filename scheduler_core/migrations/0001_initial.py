# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 10:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BroadcastCompany',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bc_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='LatestUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latest_update', models.DateTimeField()),
                ('broadcast_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler_core.BroadcastCompany')),
            ],
        ),
        migrations.CreateModel(
            name='MovieSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('ratings', models.SmallIntegerField(blank=True)),
                ('broadcast_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler_core.BroadcastCompany')),
            ],
        ),
    ]
