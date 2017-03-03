from __future__ import unicode_literals

from django.db import models


# Create your models here.
# Broadcast company
class BroadcastCompany(models.Model):
    bc_name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.bc_name


# Broadcasting schedule
class MovieSchedule(models.Model):
    broadcast_company = models.ForeignKey('BroadcastCompany', on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    ratings = models.SmallIntegerField(blank=True)

    def __unicode__(self):
        return self.broadcast_company.bc_name + "/" + self.title


# Latest update date.
class LatestUpdate(models.Model):
    broadcast_company = models.ForeignKey('BroadcastCompany', on_delete=models.CASCADE)
    latest_update = models.DateTimeField()

    def __unicode__(self):
        return self.broadcast_company + "/" + str(self.latest_update)
