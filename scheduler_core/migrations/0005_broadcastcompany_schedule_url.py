# Generated by Django 3.1.4 on 2020-12-23 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler_core', '0004_auto_20170324_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcastcompany',
            name='schedule_url',
            field=models.CharField(default=None, max_length=400, null=True),
        ),
    ]
