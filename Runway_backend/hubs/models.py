from django.contrib.gis.db import models
from auths.models import  CustomUser


class Hub(models.Model):
    hub_name = models.CharField(max_length=100,unique=True)
    address = models.CharField(max_length=200)
    location = models.PointField(geography=True, srid=4326,unique=True)
    hub_head = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='hubs')
    is_hotspot=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    number = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hub_name